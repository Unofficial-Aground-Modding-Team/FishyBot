from dataclasses import dataclass
from typing import Optional, Type
from deta_discord_interactions.models.utils import (
    LoadableDataclass,
)

# --- IMAGES ---

@dataclass
class Modio_Avatar(LoadableDataclass):
    filename: str
    original: str  # url
    thumb_50x50: str
    thumb_100x100: str

@dataclass
class Modio_HeaderImage(LoadableDataclass):
    filename: str
    original: str  # url

@dataclass
class Modio_Icon(LoadableDataclass):
    filename: str
    original: str  # url
    thumb_64x64: str
    thumb_128x128: str
    thumb_256x256: str

@dataclass
class Modio_Image(LoadableDataclass):
    filename: str
    original: str  # url
    thumb_320x180: str
    thumb_1280x720: str

@dataclass
class Modio_Logo(LoadableDataclass):
    filename: str
    original: str  # url
    thumb_320x180: str
    thumb_640x360: str
    thumb_1280x720: str

# --- USERS ---

@dataclass
class Modio_User(LoadableDataclass):
    id: int
    name_id: str  # url component
    username: str  # display name
    # display_name_portal
    date_online: int  # unix last online
    date_joined: int  # unix first joined
    avatar: Modio_Avatar
    profile_url: str  # link
    display_name_portal: str = None  # discord username, if applicable

    def __post_init__(self):
        if isinstance(self.avatar, dict):
            self.avatar = Modio_Avatar.from_dict(self.avatar)


# --- GAMES, MODS, EVENTS, COMMENTS---

@dataclass
class Modio_Game(LoadableDataclass):
    id: int
    status: int  # 0 = not accepted, 1 = accepted, 3 = deleted (2 is not documented)
    date_added: int  # registered
    date_updated: int  # last updated
    date_live: int  # set live
    presentation_option: int  # 0 = grid view, 1 = table view
    submission_option: int  # 0 = API using a tool created by the game devs, 1 = anywhere
    curation_option: int  # 0 = no curation, 1 = only mods accepting donations must be curated, 2 = all mods must be curated
    community_options: int  # 0 = all off ; 1 = comments enabled ; 2 = guides enabled ; 4 = disable website "subscribe to install" ; BITWISE
    revenue_options: int  # 0 = all off ; 1 = allow sell ; 2 = allow donations ; 4 = allow trade ; 8 = allow "control supply and scarcity" ; BITWISE
    api_access_options: int  # 0 = all off, 1 = third-paryy api access, 2 = direct downloads (opposed to "frequently changing hash") ; BITWISE
    maturity_options: int  # 0 = all off; 1 = allow mature ; 2 = adults only ; BITWISE
    ugc_name: str  # whenever to call mods "mods", "items", "addons" etc
    icon: Modio_Icon
    logo: Modio_Logo
    header: Modio_HeaderImage
    name: str
    name_id: str  # name in the URL
    summary: str
    instructions: str
    instructions_url : str
    profile_url: str
    other_urls: list
    tag_options: list
    platforms: list

    def __post_init__(self):
        if isinstance(self.icon, dict):
            self.icon = Modio_Icon.from_dict(self.icon)
        if isinstance(self.logo, dict):
            self.logo = Modio_Logo.from_dict(self.logo)
        if isinstance(self.header, dict):
            self.header = Modio_HeaderImage.from_dict(self.header)


@dataclass
class Modio_Mod(LoadableDataclass):
    id: int
    game_id: int
    status: int  # 0 hidden 1 accepted 3 deleted
    visible: int  # 0 hidden 1 public
    submitted_by: Modio_User
    date_added: int
    date_live: int
    maturity_option: int
    community_options: int
    logo: Modio_Logo
    homepage_url: str
    name: str
    name_id: str
    summary: str
    description: str  # Allows HTML
    description_plaintext: str  # plain text
    metadata_blob: str
    profile_url: str
    # These do have their specifications, but I did not bother with implementing them
    media: dict
    modfile: dict
    stats: dict
    platforms: list
    metadata_kvp: list
    tags: list
    
    def __post_init__(self):
        if isinstance(self.submitted_by, dict):
            self.submitted_by = Modio_User.from_dict(self.submitted_by)
        if isinstance(self.logo, dict):
            self.logo = Modio_Logo.from_dict(self.logo)



@dataclass
class Modio_Event(LoadableDataclass):
    id: int
    mod_id: int
    user_id: int
    date_added: int  # Unix
    event_type: str # Possible values:
    # MODFILE_CHANGED, MOD_AVAILABLE, MOD_UNAVAILABLE,
    # MOD_EDITED, MOD_DELETED, MOD_TEAM_CHANGE


@dataclass
class Modio_Comment(LoadableDataclass):
    id: int
    resource_id: int
    user: Modio_User
    date_added: int  # Unix timestamp
    reply_id: int  # parent comment ID, or 0 if not a reply
    thread_position: str  # first=01, reply=01.01, max. 3 levels
    karma: int  # can be positive or negative
    content: str

    
    def __post_init__(self):
        if isinstance(self.user, dict):
            self.user = Modio_User.from_dict(self.user)



# --- QUERY RESULTS ---

@dataclass
class Modio_QueryResults(LoadableDataclass):
    data: list
    result_count: int
    result_offset: int
    result_limit: int
    result_total: int

    def __init_subclass__(cls, result_type: Type[LoadableDataclass], database_model_name: Optional[str] = None) -> None:
        cls._result_type = result_type
        return super().__init_subclass__(database_model_name)

    def __post_init__(self):
        for i, obj in enumerate(self.data):
            if isinstance(obj, dict):
                self.data[i] = self._result_type.from_dict(obj)

@dataclass
class Modio_Games(Modio_QueryResults, result_type=Modio_Game):
    pass

@dataclass
class Modio_Mods(Modio_QueryResults, result_type=Modio_Mod):
    pass

@dataclass
class Modio_Events(Modio_QueryResults, result_type=Modio_Event):
    pass

@dataclass
class Modio_Comments(Modio_QueryResults, result_type=Modio_Comment):
    pass
