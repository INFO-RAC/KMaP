from django_auth_ldap.backend import LDAPBackend, _LDAPUser, _LDAPConfig
from infomapnode.settings import IMN_AUTH_LDAP_OU_SEPARATOR as ou_separator
from infomapnode.settings import IMN_AUTHORIZE_USERS_FROM_OU
from geonode.people.models import Profile
from geonode.groups.models import GroupProfile, GroupMember
from django.contrib.auth.models import Group


logger = _LDAPConfig.get_logger()


class IMNLDAPBackend(LDAPBackend):

    def authenticate_ldap_user(self, ldap_user, password):

        user = ldap_user.authenticate(password)
        if user:
            profile = Profile.objects.get(username=user.username)
            try:
                profile_grouplist = list(profile.group_list_all().iterator())
                for imn_group in self.get_imn_group_permissions(user):
                    grouprofile, is_created = GroupProfile.objects.get_or_create(
                        title=imn_group,
                        slug=imn_group,
                        description=imn_group,
                        access='private'
                    )
                    if grouprofile:
                        try:
                            profile_grouplist.remove(grouprofile)
                        except ValueError as e:
                            logger.debug(
                                "There aren't GroupProfile items to remove from the user"
                            )
                            pass
                    if is_created or not grouprofile.user_is_member(user):
                        member, created = GroupMember.objects.get_or_create(
                            group=grouprofile,
                            user=user,
                            role='member'
                        )
                    if not(grouprofile.group in profile.groups.all()):
                        grouprofile.group.user_set.add(user.pk)
            except TypeError as e:
                logger.debug(
                    "Retrieved InfoMapNode group permissions from OU empty for {}: {}".format(
                        user.username, e
                    )
                )
                pass
            if profile_grouplist:
                for _group_profile in profile_grouplist:
                    _group_profile.group.user_set.remove(user.pk)
                    GroupMember.objects.get(group=_group_profile, user=user).delete()
                    user.groups.remove(_group_profile.group)
        return user

    def get_group_permissions(self, user, obj=None):

        if not hasattr(user, 'ldap_user') and self.settings.AUTHORIZE_ALL_USERS:
            _LDAPUser(self, user=user)  # This sets user.ldap_user

        if hasattr(user, 'ldap_user'):
            permissions = user.ldap_user.get_group_permissions()
        else:
            permissions = set()

        return permissions

    def get_imn_group_permissions(self, user, obj=None):

        if IMN_AUTHORIZE_USERS_FROM_OU:
            imn_ldap_user = _IMNLDAPUser(self, user=user)  # This sets custom user.ldap_user

        if hasattr(user, 'ldap_user') and IMN_AUTHORIZE_USERS_FROM_OU:
            permissions = imn_ldap_user.get_group_ou_permissions()
        else:
            permissions = set()

        return permissions


class _IMNLDAPUser(_LDAPUser):

    def get_group_ou_permissions(self):
        """
        If allowed by the configuration, this returns the set of permissions
        defined by the user's OU group memberships.
        """
        if self.settings.FIND_GROUP_PERMS:
            self._group_permissions = set(self.group_ou_names)

        return self._group_permissions

    @property
    def group_ou_names(self):
        return self._get_groups_from_ou().get_ou_group_names()

    def _get_groups_from_ou(self):
        """
        Returns an _IMNLDAPUserGroups object, which can determine group
        membership.
        """
        if self._groups is None:
            self._groups = _IMNLDAPUserGroups(self.attrs)

        return self._groups


class _IMNLDAPUserGroups(object):

    """
    Represents the set of ou groups that a user belongs to.
    """
    def __init__(self, attrs):
        self.separator = ou_separator
        self._attrs = attrs
        self._group_ou_names = None

    def get_ou_group_names(self):
        """
        Returns the set of Django group names that this user belongs to by
        parsing OU value of separated strings.
        """
        if self._group_ou_names is None:
            try:
                self._group_ou_names = self._attrs["ou"][0].split(
                    self.separator
                )
            except KeyError as e:
                logger.debug(
                    "Retrieve OU attribute failed for {}: {}".format(
                        self._attrs["uid"], e
                    )
                )

        return self._group_ou_names

