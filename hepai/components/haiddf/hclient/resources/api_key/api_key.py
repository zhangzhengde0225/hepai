

from typing import Union, Dict
from ...openai_api import Stream
from .._resource import SyncAPIResource

from ..._return_class import (
    HAPIKeyListPage,
)
from ..._related_class import (
    APIKeyInfo, APIKeyDeletedInfo,
)

class Key(SyncAPIResource):

    @property
    def prefix(self) -> str:
        return "/key"
    
    def list_api_keys(self):
        return self._get(
            f"{self.prefix}/list_api_keys",
            cast_to=HAPIKeyListPage,
        )
    
    def create_api_key(
            self,
            *,
            key_name: str = "Default",
            valid_time: int = 30,
            user_id: str = None,
            umt_id: str = None,
            allowed_models: Union[str, Dict] = "all",
            remarks: str = "",
            ):
        payload = {
            "key_name": key_name,
            "valid_time": valid_time,
            "user_id": user_id,
            "umt_id": umt_id,
            "allowed_models": allowed_models,
            "remarks": remarks,
        }
        return self._post(
            f"{self.prefix}/create_api_key",
            body=payload,
            cast_to=APIKeyInfo,
        )
    
    def delete_api_key(self, api_key_id: str):
        payload = {
            "api_key_id": api_key_id,
        }
        return self._post(
            f"{self.prefix}/delete_api_key",
            body=payload,
            cast_to=APIKeyDeletedInfo,
        )
    
    def get_info(self, api_key: str):
        payload = {
            "api_key": api_key,
        }
        return self._post(
            f"{self.prefix}/info",
            body=payload,
        )
