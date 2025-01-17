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

"""Integration tests for tightlock-api container."""

import ast
from urllib import parse

import pytest


def test_initial_config(helpers):
  """Verifies if an initial config was provided at application startup."""
  request_session, api_url = helpers.get_tightlock_api_client()
  config = request_session.get(parse.urljoin(api_url, "api/v1/configs")).json()
  assert config[0]["label"] == "Initial Config"


def test_connect_authentication(helpers):
  """Verifies if connect/ endpoint is properly authenticated."""
  request_session, api_url = helpers.get_tightlock_api_client()
  request_session.headers.update({"X-API-Key": "fake-api-key"})
  response = request_session.post(parse.urljoin(api_url, "api/v1/connect"))
  assert response.status_code == 401


@pytest.mark.parametrize(
    "test_location,expected_result",
    [("integration_test.csvh", True), ("non_existent.file", False)],
)
def test_validate_source(helpers, test_location, expected_result):
  request_session, api_url = helpers.get_tightlock_api_client()
  response = request_session.post(
      parse.urljoin(api_url, f"api/v1/sources/local_file:validate"),
      json={"value": {"location": test_location}},
  )
  if response.status_code != 200:
    pytest.fail(response.text)
  validation_result = response.json()
  assert validation_result["is_valid"] == expected_result


def test_validate_destination(helpers):
  request_session, api_url = helpers.get_tightlock_api_client()
  response = request_session.post(
      parse.urljoin(api_url, f"api/v1/destinations/ga4mp:validate"),
      json={
          "value": {
              "payload_type": "firebase",
              "api_secret": "test",
              "firebase_app_id": "test",
          }
      },
  )
  if response.status_code != 200:
    pytest.fail(response.text)
  validation_result = response.json()
  assert validation_result["is_valid"]
