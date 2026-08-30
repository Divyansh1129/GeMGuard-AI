"""Registry-integration boundary.

Government registry results are intentionally not emulated. Production callers
must use an authorised GSTN/GSP, NSDL/Protean, Udyam, EPFO or ESIC connector.
"""


class RegistryIntegrationUnavailable(RuntimeError):
    pass


def require_authorised_registry_integration(registry: str) -> None:
    raise RegistryIntegrationUnavailable(
        f"{registry} verification requires an authorised government or licensed-provider integration."
    )
