"""High-level Hyperliquid exchange client with async retry helpers.

This module wraps the Hyperliquid `Exchange` and `Info` SDK classes to provide a
single entry point for submitting trades, managing orders, and retrieving market
state.  It normalizes retry behaviour, adds logging, and caches metadata so that
the trading agent can depend on predictable, non-blocking IO.
"""

import asyncio
import logging
import aiohttp
from typing import TYPE_CHECKING
from src.config_loader import CONFIG
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants  # For MAINNET/TESTNET
from eth_account import Account as _Account
from eth_account.signers.local import LocalAccount
from websocket._exceptions import WebSocketConnectionClosedException
import socket

if TYPE_CHECKING:
    # Type stubs for linter - eth_account's type stubs are incorrect
    class Account:
        @staticmethod
        def from_key(_private_key: str) -> LocalAccount: ...
        @staticmethod
        def from_mnemonic(_mnemonic: str) -> LocalAccount: ...
        @staticmethod
        def enable_unaudited_hdwallet_features() -> None: ...
else:
    Account = _Account

class HyperliquidAPI:
    """Facade around Hyperliquid SDK clients with async convenience methods.

    The class owns wallet credentials, connection configuration, and provides
    coroutine helpers that keep retry semantics and logging consistent across
    the trading agent.
    """

    def __init__(self):
        """Initialize wallet credentials and instantiate exchange clients.

        Raises:
            ValueError: If neither a private key nor mnemonic is present in the
                configuration.
        """
        self._meta_cache = None
        if "hyperliquid_private_key" in CONFIG and CONFIG["hyperliquid_private_key"]:
            self.wallet = Account.from_key(CONFIG["hyperliquid_private_key"])
        elif "mnemonic" in CONFIG and CONFIG["mnemonic"]:
            Account.enable_unaudited_hdwallet_features()
            self.wallet = Account.from_mnemonic(CONFIG["mnemonic"])
        else:
            raise ValueError("Either HYPERLIQUID_PRIVATE_KEY/LIGHTER_PRIVATE_KEY or MNEMONIC must be provided")
        # Choose base URL: allow override via env-config; fallback to network selection
        network = (CONFIG.get("hyperliquid_network") or "mainnet").lower()
        base_url = CONFIG.get("hyperliquid_base_url")
        if not base_url:
            if network == "testnet":
                base_url = getattr(constants, "TESTNET_API_URL", constants.MAINNET_API_URL)
            else:
                base_url = constants.MAINNET_API_URL
        self.base_url = base_url
        self._build_clients()

    def _build_clients(self):
        """Instantiate exchange and info client instances for the active base URL."""
        self.info = Info(self.base_url)
        self.exchange = Exchange(self.wallet, self.base_url)

    def _reset_clients(self):
        """Recreate SDK clients after connection failures while logging failures."""
        try:
            self._build_clients()
            logging.warning("Hyperliquid clients re-instantiated after connection issue")
        except (ValueError, AttributeError, RuntimeError) as e:
            logging.error("Failed to reset Hyperliquid clients: %s", e)

    async def _retry(self, fn, *args, max_attempts: int = 3, backoff_base: float = 0.5, reset_on_fail: bool = True, to_thread: bool = True, **kwargs):
        """Retry helper with exponential backoff and optional thread offloading.

        Args:
            fn: Callable to invoke, either sync (supports `asyncio.to_thread`) or
                async depending on ``to_thread``. The callable should raise
                exceptions rather than returning sentinel values.
            *args: Positional arguments forwarded to ``fn``.
            max_attempts: Maximum number of attempts before surfacing the last
                exception.
            backoff_base: Initial delay in seconds, doubled after each failure.
            reset_on_fail: Whether to rebuild Hyperliquid clients after a
                failure.
            to_thread: If ``True`` the callable is executed in a worker thread.
            **kwargs: Keyword arguments forwarded to ``fn``.

        Returns:
            Result produced by ``fn``.

        Raises:
            Exception: Propagates any exception raised by ``fn`` after retries.
        """
        last_err = None
        for attempt in range(max_attempts):
            try:
                if to_thread:
                    return await asyncio.to_thread(fn, *args, **kwargs)
                return await fn(*args, **kwargs)
            except (WebSocketConnectionClosedException, aiohttp.ClientError, ConnectionError, TimeoutError, socket.timeout) as e:
                last_err = e
                logging.warning("HL call failed (attempt %s/%s): %s", attempt + 1, max_attempts, e)
                if reset_on_fail:
                    self._reset_clients()
                await asyncio.sleep(backoff_base * (2 ** attempt))
                continue
            except (RuntimeError, ValueError, KeyError, AttributeError) as e:
                # Unknown errors: don't spin forever, but allow a quick reset once
                last_err = e
                logging.warning("HL call unexpected error (attempt %s/%s): %s", attempt + 1, max_attempts, e)
                if reset_on_fail and attempt == 0:
                    self._reset_clients()
                    await asyncio.sleep(backoff_base)
                    continue
                break
        raise last_err if last_err else RuntimeError("Hyperliquid retry: unknown error")

    def round_size(self, asset, amount):
        """Round order size to the asset precision defined by market metadata.

        Args:
            asset: Symbol of the market whose contract size we are rounding to.
            amount: Desired contract size before rounding.

        Returns:
            The input ``amount`` rounded to the market's ``szDecimals`` precision.
        """
        meta = self._meta_cache[0] if hasattr(self, '_meta_cache') and self._meta_cache else None
        if meta:
            universe = meta.get("universe", [])
            asset_info = next((u for u in universe if u.get("name") == asset), None)
            if asset_info:
                decimals = asset_info.get("szDecimals", 8)
                return round(amount, decimals)
        return round(amount, 8)

    async def place_buy_order(self, asset, amount, slippage=0.01):
        """Submit a market buy order with exchange-side rounding and retry logic.

        Args:
            asset: Market symbol to open.
            amount: Contract size to open before rounding.
            slippage: Maximum acceptable slippage expressed as a decimal.

        Returns:
            Raw SDK response from :meth:`Exchange.market_open`.
        """
        amount = self.round_size(asset, amount)
        return await self._retry(lambda: self.exchange.market_open(asset, True, amount, None, slippage))

    async def place_sell_order(self, asset, amount, slippage=0.01):
        """Submit a market sell order with exchange-side rounding and retry logic.

        Args:
            asset: Market symbol to open.
            amount: Contract size to open before rounding.
            slippage: Maximum acceptable slippage expressed as a decimal.

        Returns:
            Raw SDK response from :meth:`Exchange.market_open`.
        """
        amount = self.round_size(asset, amount)
        return await self._retry(lambda: self.exchange.market_open(asset, False, amount, None, slippage))

    async def place_take_profit(self, asset, is_buy, amount, tp_price):
        """Create a reduce-only trigger order that executes a take-profit exit.

        Args:
            asset: Market symbol to trade.
            is_buy: ``True`` if the original position is long; dictates close
                direction.
            amount: Contract size to close.
            tp_price: Trigger price for the take-profit order.

        Returns:
            Raw SDK response from `Exchange.order`.
        """
        amount = self.round_size(asset, amount)
        order_type = {"trigger": {"triggerPx": tp_price, "isMarket": True, "tpsl": "tp"}}
        return await self._retry(lambda: self.exchange.order(asset, not is_buy, amount, tp_price, order_type, True))

    async def place_stop_loss(self, asset, is_buy, amount, sl_price):
        """Create a reduce-only trigger order that executes a stop-loss exit.

        Args:
            asset: Market symbol to trade.
            is_buy: ``True`` if the original position is long; dictates close
                direction.
            amount: Contract size to close.
            sl_price: Trigger price for the stop-loss order.

        Returns:
            Raw SDK response from `Exchange.order`.
        """
        amount = self.round_size(asset, amount)
        order_type = {"trigger": {"triggerPx": sl_price, "isMarket": True, "tpsl": "sl"}}
        return await self._retry(lambda: self.exchange.order(asset, not is_buy, amount, sl_price, order_type, True))

    async def cancel_order(self, asset, oid):
        """Cancel a single order by identifier for a given asset.

        Args:
            asset: Market symbol associated with the order.
            oid: Hyperliquid order identifier to cancel.

        Returns:
            Raw SDK response from :meth:`Exchange.cancel`.
        """
        return await self._retry(lambda: self.exchange.cancel(asset, oid))

    async def cancel_all_orders(self, asset):
        """Cancel every open order for ``asset`` owned by the configured wallet."""
        try:
            open_orders = await self._retry(lambda: self.info.frontend_open_orders(self.wallet.address))
            for order in open_orders:
                if order.get("coin") == asset:
                    oid = order.get("oid")
                    if oid:
                        await self.cancel_order(asset, oid)
            return {"status": "ok", "cancelled_count": len([o for o in open_orders if o.get("coin") == asset])}
        except (RuntimeError, ValueError, KeyError, ConnectionError) as e:
            logging.error("Cancel all orders error for %s: %s", asset, e)
            return {"status": "error", "message": str(e)}

    async def get_open_orders(self):
        """Fetch and normalize open orders associated with the wallet.

        Returns:
            List of order dictionaries augmented with ``triggerPx`` when present.
        """
        try:
            orders = await self._retry(lambda: self.info.frontend_open_orders(self.wallet.address))
            # Normalize trigger price if present in orderType
            for o in orders:
                try:
                    ot = o.get("orderType")
                    if isinstance(ot, dict) and "trigger" in ot:
                        trig = ot.get("trigger") or {}
                        if "triggerPx" in trig:
                            o["triggerPx"] = float(trig["triggerPx"])
                except (ValueError, KeyError, TypeError):
                    continue
            return orders
        except (RuntimeError, ValueError, KeyError, ConnectionError) as e:
            logging.error("Get open orders error: %s", e)
            return []

    async def get_recent_fills(self, limit: int = 50):
        """Return the most recent fills when supported by the SDK variant.

        Args:
            limit: Maximum number of fills to return.

        Returns:
            List of fill dictionaries or an empty list if unsupported.
        """
        try:
            # Some SDK versions expose user_fills; fall back gracefully if absent
            if hasattr(self.info, 'user_fills'):
                fills = await self._retry(lambda: self.info.user_fills(self.wallet.address))
            elif hasattr(self.info, 'fills'):
                fills = await self._retry(lambda: self.info.fills(self.wallet.address))
            else:
                return []
            if isinstance(fills, list):
                return fills[-limit:]
            return []
        except (RuntimeError, ValueError, KeyError, ConnectionError, AttributeError) as e:
            logging.error("Get recent fills error: %s", e)
            return []

    def extract_oids(self, order_result):
        """Extract resting or filled order identifiers from an exchange response.

        Args:
            order_result: Raw order response payload returned by the exchange.

        Returns:
            List of order identifiers present in resting or filled status entries.
        """
        oids = []
        try:
            statuses = order_result["response"]["data"]["statuses"]
            for st in statuses:
                if "resting" in st and "oid" in st["resting"]:
                    oids.append(st["resting"]["oid"])
                if "filled" in st and "oid" in st["filled"]:
                    oids.append(st["filled"]["oid"])
        except (KeyError, TypeError, ValueError):
            pass
        return oids

    async def get_user_state(self):
        """Retrieve wallet state with enriched position PnL calculations.

        Returns:
            Dictionary with ``balance``, ``total_value``, and ``positions``.
        """
        state = await self._retry(lambda: self.info.user_state(self.wallet.address))
        positions = state.get("assetPositions", [])
        total_value = float(state.get("accountValue", 0.0))
        enriched_positions = []
        for pos_wrap in positions:
            pos = pos_wrap["position"]
            entry_px = float(pos.get("entryPx", 0) or 0)
            size = float(pos.get("szi", 0) or 0)
            side = "long" if size > 0 else "short"
            current_px = await self.get_current_price(pos["coin"]) if entry_px and size else 0.0
            pnl = (current_px - entry_px) * abs(size) if side == "long" else (entry_px - current_px) * abs(size)
            pos["pnl"] = pnl
            pos["notional_entry"] = abs(size) * entry_px
            enriched_positions.append(pos)
        balance = float(state.get("withdrawable", 0.0))
        if not total_value:
            total_value = balance + sum(max(p.get("pnl", 0.0), 0.0) for p in enriched_positions)
        return {"balance": balance, "total_value": total_value, "positions": enriched_positions}

    async def get_current_price(self, asset):
        """Return the latest mid-price for ``asset``.

        Args:
            asset: Market symbol to query.

        Returns:
            Mid-price as a float, or ``0.0`` when unavailable.
        """
        mids = await self._retry(self.info.all_mids)
        return float(mids.get(asset, 0.0))

    async def get_meta_and_ctxs(self):
        """Return cached meta/context information, fetching once per lifecycle.

        Returns:
            Cached metadata response as returned by
            :meth:`Info.meta_and_asset_ctxs`.
        """
        if not self._meta_cache:
            response = await self._retry(self.info.meta_and_asset_ctxs)
            self._meta_cache = response
        return self._meta_cache

    async def get_open_interest(self, asset):
        """Return open interest for ``asset`` if it exists in cached metadata.

        Args:
            asset: Market symbol to query.

        Returns:
            Rounded open interest or ``None`` if unavailable.
        """
        try:
            data = await self.get_meta_and_ctxs()
            if isinstance(data, list) and len(data) >= 2:
                meta, asset_ctxs = data[0], data[1]
                universe = meta.get("universe", [])
                asset_idx = next((i for i, u in enumerate(universe) if u.get("name") == asset), None)
                if asset_idx is not None and asset_idx < len(asset_ctxs):
                    oi = asset_ctxs[asset_idx].get("openInterest")
                    return round(float(oi), 2) if oi else None
            return None
        except (RuntimeError, ValueError, KeyError, ConnectionError, TypeError) as e:
            logging.error("OI fetch error for %s: %s", asset, e)
            return None

    async def get_funding_rate(self, asset):
        """Return the most recent funding rate for ``asset`` if available.

        Args:
            asset: Market symbol to query.

        Returns:
            Funding rate as a float or ``None`` when not present.
        """
        try:
            data = await self.get_meta_and_ctxs()
            if isinstance(data, list) and len(data) >= 2:
                meta, asset_ctxs = data[0], data[1]
                universe = meta.get("universe", [])
                asset_idx = next((i for i, u in enumerate(universe) if u.get("name") == asset), None)
                if asset_idx is not None and asset_idx < len(asset_ctxs):
                    funding = asset_ctxs[asset_idx].get("funding")
                    return round(float(funding), 8) if funding else None
            return None
        except (RuntimeError, ValueError, KeyError, ConnectionError, TypeError) as e:
            logging.error("Funding fetch error for %s: %s", asset, e)
            return None
