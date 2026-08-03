"""SNMP client wrapper around pysnmp (optional dependency)."""

from __future__ import annotations

from typing import Any, List

from core.exceptions import SNMPError


class SNMPClient:
    """Performs SNMP get/walk operations against a network device."""

    def __init__(self, host: str, community: str = "public", port: int = 161) -> None:
        self.host = host
        self.community = community
        self.port = port

    def _pysnmp(self) -> Any:
        try:
            import pysnmp.hlapi as hlapi  # type: ignore
        except ImportError as exc:
            raise SNMPError(
                "pysnmp is required for SNMP operations: pip install pysnmp"
            ) from exc
        return hlapi

    def get(self, oid: str) -> Any:
        hlapi = self._pysnmp()
        error_indication, error_status, error_index, var_binds = next(
            hlapi.getCmd(
                hlapi.SnmpEngine(),
                hlapi.CommunityData(self.community),
                hlapi.UdpTransportTarget((self.host, self.port)),
                hlapi.ContextData(),
                hlapi.ObjectType(hlapi.ObjectIdentity(oid)),
            )
        )
        if error_indication:
            raise SNMPError(str(error_indication))
        if error_status:
            raise SNMPError(f"{error_status.prettyPrint()} at {error_index}")
        return var_binds[0][1].prettyPrint()

    def walk(self, oid: str) -> List[Any]:
        hlapi = self._pysnmp()
        results: List[Any] = []
        for error_indication, error_status, error_index, var_binds in hlapi.nextCmd(
            hlapi.SnmpEngine(),
            hlapi.CommunityData(self.community),
            hlapi.UdpTransportTarget((self.host, self.port)),
            hlapi.ContextData(),
            hlapi.ObjectType(hlapi.ObjectIdentity(oid)),
        ):
            if error_indication:
                raise SNMPError(str(error_indication))
            if error_status:
                raise SNMPError(f"{error_status.prettyPrint()} at {error_index}")
            for var_bind in var_binds:
                results.append(var_bind[1].prettyPrint())
        return results
