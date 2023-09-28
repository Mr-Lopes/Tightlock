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
 limitations under the License.
 """

from airflow.hooks.postgres_hook import PostgresHook
import json
import tempfile
from typing import Any, Dict, List, Mapping, Optional, Sequence

from google.auth.exceptions import RefreshError
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from pydantic import Field
from dags.protocols.source_proto import SourceProto
from utils import ProtocolSchema, SchemaUtils, ValidationResult

DATA_FIELD_OFFSET = 1
RETRY_FIELD_OFFSET = 2


# TODO(caiotomazelli): Hide this from the UI.
class Source(SourceProto):
  """Implements SourceProto protocol for Retrying (should not be used directly)."""
  IS_RETRY_SOURCE = True

  def __init__(self, config: Mapping[str, Any]):
    self.connection_id=config['connection_id']
    self.retry_count=config['retry_count']
    self.batch_size=config['batch_size']

    self.data = self._get_retry_data(config['connection_id'], config['uuid'])

  def _get_retry_data(self, connection_id, uuid) -> List[Mapping[str, Any]]:
    """Gets retry data from the database."""
    sql = f'''SELECT data
              FROM Retry
              WHERE connection_id = %s AND uuid = %s
              ORDER BY next_try ASC
              LIMIT 1'''
    pg_hook = PostgresHook(postgres_conn_id="tightlock_retry",)
    cursor = pg_hook.get_conn().cursor()
    cursor.execute(sql, (connection_id, uuid))
    raw = cursor.fetchone()[DATA_FIELD_OFFSET]
    data = json.loads(raw)
    return data

  def get_data(
      self,
      fields: Sequence[str],
      offset: int,
      limit: int,
      reusable_credentials: Optional[Sequence[Mapping[str, Any]]],
  ) -> List[Mapping[str, Any]]:
    """`get_data()` implemention for Retry source."""
    return self.data[offset:offset + limit]

  @staticmethod
  def schema() -> Optional[ProtocolSchema]:
    return ProtocolSchema(
        "retry",
        [
            ("connection_id", str, Field(description="Connection id.",)),
            ("uuid", str, Field(description="Universally unique id.",)),
            ("retry_count", int, Field(description="Retry count.",)),
        ]
    )

  def validate(self) -> ValidationResult:
    return ValidationResult(True, [])