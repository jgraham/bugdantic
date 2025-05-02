import enum
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, MutableMapping, Optional, Sequence
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ConfigDict

Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None

QueryValue = Optional[str | int | float | bool]
QueryParams = Mapping[str, QueryValue | Sequence[QueryValue]]


class BugzillaError(Exception):
    pass


class UserGroup(BaseModel):
    id: int
    name: str
    description: str


class UserSearch(BaseModel):
    id: int
    name: str
    query: str


class User(BaseModel):
    id: int
    real_name: str
    email: str
    name: str
    can_login: Optional[bool] = None
    email_enabled: Optional[bool] = None
    login_denied_text: Optional[str] = None
    groups: Optional[list[UserGroup]] = None
    saved_searches: Optional[list[UserSearch]] = None
    saved_reports: Optional[list[UserSearch]] = None


# Data models for getting bugs


class Flag(BaseModel):
    id: int
    name: str
    type_id: int
    creation_date: datetime
    modification_date: datetime
    status: str
    setter: str
    requestee: str


class Change(BaseModel):
    field_name: str
    removed: str
    added: str
    attachment_id: Optional[int] = None


class History(BaseModel):
    when: datetime
    who: str
    changes: list[Change]


class Bug(BaseModel):
    actual_time: Optional[float] = None
    alias: Optional[list[str]] = None
    assigned_to: Optional[str] = None
    assigned_to_detail: Optional[User] = None
    blocks: Optional[list[int]] = None
    cc: Optional[list[str]] = None
    cc_detail: Optional[list[User]] = None
    classification: Optional[str] = None
    component: Optional[str] = None
    creation_time: Optional[datetime] = None
    creator: Optional[str] = None
    creator_detail: Optional[User] = None
    deadline: Optional[str] = None
    depends_on: Optional[list[int]] = None
    dupe_of: Optional[int] = None
    estimated_time: Optional[float] = None
    flags: Optional[list[Flag]] = None
    groups: Optional[list[str]] = None
    id: Optional[int] = None
    is_cc_accessible: Optional[bool] = None
    is_confirmed: Optional[bool] = None
    is_open: Optional[bool] = None
    is_creator_accessible: Optional[bool] = None
    history: Optional[list[History]] = None
    keywords: Optional[list[str]] = None
    last_change_time: Optional[datetime] = None
    op_sys: Optional[str] = None
    platform: Optional[str] = None
    priority: Optional[str] = None
    product: Optional[str] = None
    qa_contact: Optional[str] = None
    qa_contact_detail: Optional[User] = None
    remaining_time: Optional[float] = None
    resolution: Optional[str] = None
    see_also: Optional[list[str]] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    target_milestone: Optional[str] = None
    update_token: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    whiteboard: Optional[str] = None

    # BMO specific custom fields
    cf_last_resolved: Optional[datetime] = None
    cf_size_estimate: Optional[str] = None
    cf_user_story: Optional[str] = None
    cf_webcompat_priority: Optional[str] = None
    cf_webcompat_score: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class BugSearch(BaseModel):
    faults: Optional[list[Any]] = None
    bugs: Optional[list[Bug]] = None


# Data model for bug history


class BugHistory(BaseModel):
    id: int
    history: list[History]
    alias: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class BugsHistory(BaseModel):
    faults: Optional[list[Any]] = None
    bugs: Optional[list[BugHistory]] = None


# Data models for update requests


class BugRelationUpdate(BaseModel):
    add: Optional[list[int]] = None
    remove: Optional[list[int]] = None
    set: Optional[list[int]] = None


class BugKeywordsUpdate(BaseModel):
    add: Optional[list[str]] = None
    remove: Optional[list[str]] = None
    set: Optional[list[str]] = None


class BugCcUpdate(BaseModel):
    add: Optional[list[str]] = None
    remove: Optional[list[str]] = None


class BugGroupsUpdate(BaseModel):
    add: Optional[list[str]] = None
    remove: Optional[list[str]] = None


class BugSeeAlsoUpdate(BaseModel):
    add: Optional[list[str]] = None
    remove: Optional[list[str]] = None


class Comment(BaseModel):
    body: str
    is_private: Optional[bool] = False


class FlagChange(BaseModel):
    name: Optional[str] = None
    type_id: Optional[int] = None
    status: str
    requestee: Optional[str] = None
    id: Optional[int] = None
    new: Optional[bool] = None


class Priority(enum.StrEnum):
    unset = "--"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"


class Severity(enum.StrEnum):
    unset = "--"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"
    not_applicable = "N/A"


class WebcompatPriority(enum.StrEnum):
    unset = "---"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    requested = "?"


class SizeEstimate(enum.StrEnum):
    unset = "---"
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class BugUpdate(BaseModel):
    ids: Optional[list[int]] = None
    id_or_alias: Optional[int | str] = None

    alias: Optional[list[Any]] = None
    assigned_to: Optional[str] = None
    blocks: Optional[BugRelationUpdate] = None
    depends_on: Optional[BugRelationUpdate] = None
    cc: Optional[BugCcUpdate] = None
    is_cc_accessible: Optional[bool] = None
    comment: Optional[Comment] = None
    comment_is_private: Optional[dict[int, bool]] = None
    component: Optional[str] = None
    deadline: Optional[datetime] = None
    dupe_of: Optional[int] = None
    estimated_time: Optional[float] = None
    flags: Optional[FlagChange] = None
    groups: Optional[BugGroupsUpdate] = None
    keywords: Optional[BugKeywordsUpdate] = None
    op_sys: Optional[str] = None
    platform: Optional[str] = None
    priority: Optional[Priority] = None
    product: Optional[str] = None
    qa_contact: Optional[str] = None
    is_creator_accessible: Optional[bool] = None
    remaining_time: Optional[float] = None
    reset_assigned_to: Optional[bool] = None
    reset_qa_contact: Optional[bool] = None
    resolution: Optional[str] = None
    see_also: Optional[BugSeeAlsoUpdate] = None
    severity: Optional[Severity] = None
    summary: Optional[str] = None
    target_milestone: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
    whiteboard: Optional[str] = None
    work_time: Optional[str] = None

    # BMO specific custom fields
    cf_size_estimate: Optional[SizeEstimate] = None
    cf_user_story: Optional[str] = None
    cf_webcompat_priority: Optional[WebcompatPriority] = None
    cf_webcompat_score: Optional[str] = None


class BugChange(BaseModel):
    added: Any
    removed: Any


class BugUpdateResponse(BaseModel):
    id: int
    last_change_time: datetime
    changes: dict[str, BugChange]
    alias: Optional[str] = None


class BugsUpdateResponse(BaseModel):
    bugs: Optional[list[BugUpdateResponse]] = None
    faults: Optional[list[Any]] = None


@dataclass
class BugzillaConfig:
    base_url: str
    api_key: Optional[str] = None
    request_timeout: Optional[int] = 60
    allow_writes: bool = False
    # Number of times to retry a request if there's a 503 error
    max_retries: int = 1


class Bugzilla:
    def __init__(self, config: BugzillaConfig):
        self.config = config
        headers = (
            {"X-Bugzilla-API-Key": self.config.api_key}
            if self.config.api_key is not None
            else None
        )

        self.client = httpx.Client(
            http2=True, timeout=config.request_timeout, headers=headers
        )

    def request(
        self,
        method: str,
        path: str,
        include_fields: Optional[list[str]] = None,
        exclude_fields: Optional[list[str]] = None,
        params: Optional[QueryParams] = None,
        headers: Optional[dict[str, str]] = None,
        json_body: Optional[MutableMapping[str, Json]] = None,
    ) -> Mapping[str, Json]:
        if params is None:
            params = {}
        else:
            params = {**params}

        if include_fields is not None:
            params["include_fields"] = ",".join(include_fields)

        if exclude_fields is not None:
            params["exclude_fields"] = ",".join(exclude_fields)

        if path.startswith("/"):
            path = path[1:]

        url = urljoin(self.config.base_url, f"/rest/{path}")

        if self.config.allow_writes or method in {"GET", "OPTIONS", "HEAD"}:
            retry = 0
            while retry <= self.config.max_retries:
                retry += 1
                response = self.client.request(
                    method, url, params=params, headers=headers, json=json_body
                )
                if response.status_code != 503:
                    break
            try:
                response.raise_for_status()
            except Exception as e:
                msg = "Request failed"
                json_resp = response.json()
                if json_resp:
                    msg += f"\n{json_resp.get('message')}"
                logging.error(msg)
                raise e
            return response.json()
        else:
            logging.info(f"""Not updating, would send {method} request to {path} with body:
{json.dumps(json_body)}
===
""")
            return {}

    def bug(
        self, bug_id: int, include_fields: Optional[list[str]] = None
    ) -> Optional[Bug]:
        """Get a single bug specified by id"""
        search_result = BugSearch.model_validate(
            self.request("GET", f"bug/{bug_id}", include_fields=include_fields)
        )
        if search_result.faults:
            raise BugzillaError(search_result.faults)
        bugs = search_result.bugs
        if not bugs:
            return None
        assert len(bugs) == 1
        return bugs[0]

    def bugs(
        self,
        bug_ids: Sequence[int],
        include_fields: Optional[list[str]] = None,
        page_size: int = 100,
    ) -> list[Bug]:
        """Get multiple bugs specified by id"""
        results: list[Bug] = []
        for bug_ids_chunk in [
            bug_ids[n : n + page_size] for n in range(0, len(bug_ids), page_size)
        ]:
            results.extend(
                self.search(
                    {"id": ",".join(str(id) for id in bug_ids_chunk)},
                    include_fields=include_fields,
                )
            )
        return results

    def bug_history(
        self, bug_id: int, new_since: Optional[datetime] = None
    ) -> BugHistory:
        """Get the history of a single bug"""
        params = {}
        if new_since is not None:
            params["new_since"] = new_since.strftime("%Y-%m-%dT%H:%M:%SZ")
        query_result = BugsHistory.model_validate(
            self.request("GET", f"bug/{bug_id}/history", params=params)
        )
        if query_result.faults:
            raise BugzillaError(query_result.faults)
        bugs = query_result.bugs
        if bugs is None:
            raise BugzillaError("Empty bugs list but no faults")
        assert len(bugs) == 1
        return bugs[0]

    def search(
        self,
        query: QueryParams,
        include_fields: Optional[list[str]] = None,
        page_size: int = 100,
    ) -> list[Bug]:
        """Search for bugs using the bugzilla query API"""
        query = {**query}
        paginate = False
        offset = 0
        if "limit" not in query and "offset" not in query and page_size > 0:
            query["limit"] = str(page_size)
            query["offset"] = "0"
            paginate = True

        results: list[Bug] = []
        while True:
            response = self.request(
                "GET", "bug", params=query, include_fields=include_fields
            )
            search_result = BugSearch.model_validate(response)
            if search_result.faults:
                raise BugzillaError(search_result.faults)
            if search_result.bugs is not None:
                results.extend(search_result.bugs)
                if not paginate or len(search_result.bugs) < page_size:
                    break
            else:
                logging.error(
                    f"Invalid bugzilla response object: {json.dumps(response)}"
                )
                raise BugzillaError("Response contained neither bugs nor faults fields")

            offset += page_size
            query["offset"] = str(offset)

        return results

    def update_bugs(
        self, update_params: BugUpdate, bug_id: Optional[int] = None
    ) -> list[BugUpdateResponse]:
        """Update one or more bugs"""
        if bug_id is None:
            if update_params.ids:
                id_str = str(update_params.ids[0])
            elif update_params.id_or_alias:
                id_str = str(update_params.id_or_alias)
            else:
                raise ValueError("Missing bug ids to update")
        else:
            id_str = str(bug_id)

        # Apparently there has to be a bug id in the URL
        path = f"bug/{id_str}"

        json_body = update_params.model_dump(exclude_none=True)

        response = self.request("PUT", path, json_body=json_body)

        if self.config.allow_writes:
            update_result = BugsUpdateResponse.model_validate(response)
            if update_result.faults:
                raise BugzillaError(update_result.faults)
            if update_result.bugs is None:
                logging.error(
                    f"Invalid bugzilla response object: {json.dumps(response)}"
                )
                raise BugzillaError("Response contained neither bugs nor faults fields")
            return update_result.bugs

        return []
