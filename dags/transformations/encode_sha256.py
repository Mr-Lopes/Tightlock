"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

from hashlib import sha256

from schemas import ProtocolSchema

from pydantic import Field
from typing import Any, Dict, List, Mapping, Optional


class Transformation:
  """Implements SHA256 Encoding value transformation."""
  def __init__(self, config: Dict[str, Any]):
    self.field_name = config["field_name"]

  def pre_transform(
      self,
      fields: List[str]
  ) -> List[str]:
    return fields

  def post_transform(
      self,
      input_data: List[Mapping[str, Any]]
  ) -> List[Mapping[str, Any]]:
    for row_data in input_data:
      self._encode_field(row_data)
    return input_data

  def _encode_field(self, row_data: Mapping[str, Any]) -> None:
    if self.field_name not in row_data:
      raise ValueError(
          f"Transformation error:  Could not find field '{self.field_name}' to SHA encode."
      )

    value = row_data[self.field_name]
    if value:
      hash = sha256(value.encode('utf-8'))
      row_data[self.field_name] = hash.hexdigest()

  @staticmethod
  def schema() -> Optional[ProtocolSchema]:
    return ProtocolSchema(
        "encode_sha256",
        [
            ("field_name", str, Field(
                description="The name of field in the source dataset to encode.",
                validation="^[a-zA-Z0-9_]{1,1024}$")),
        ]
    )