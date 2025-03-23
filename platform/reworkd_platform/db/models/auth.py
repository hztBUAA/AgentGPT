from sqlalchemy import DateTime, String
from sqlalchemy.orm import mapped_column

from reworkd_platform.db.base import TrackedModel


class Organization(TrackedModel):
    __tablename__ = "organization"

    name = mapped_column(String(255), nullable=False)
    created_by = mapped_column(String(255), nullable=False)


class OrganizationUser(TrackedModel):
    __tablename__ = "organization_user"

    user_id = mapped_column(String(255), nullable=False)
    organization_id = mapped_column(String(36), nullable=False)
    role = mapped_column(String(50), nullable=False, default="member")


class OauthCredentials(TrackedModel):
    __tablename__ = "oauth_credentials"

    user_id = mapped_column(String(255), nullable=False)
    organization_id = mapped_column(String(36), nullable=True)
    provider = mapped_column(String(50), nullable=False)
    state = mapped_column(String(100), nullable=False)
    redirect_uri = mapped_column(String(1024), nullable=False)

    # Post-installation
    token_type = mapped_column(String(50), nullable=True)
    access_token_enc = mapped_column(String(2048), nullable=True)
    access_token_expiration = mapped_column(DateTime, nullable=True)
    refresh_token_enc = mapped_column(String(2048), nullable=True)
    scope = mapped_column(String(1024), nullable=True)
