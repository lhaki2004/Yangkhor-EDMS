from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.authentication.link_conditions import (
    condition_is_current_user, condition_not_is_current_user,
    condition_user_is_authenticated
)
from mayan.apps.navigation.classes import Link
from mayan.apps.navigation.utils import get_content_type_kwargs_factory

from .icons import (
    icon_event_types_subscriptions_list,
    icon_object_event_list, icon_object_event_list_clear,
    icon_object_event_list_export, icon_event_list, icon_event_list_clear,
    icon_event_list_export, icon_notification_mark_read,
    icon_notification_mark_read_all,
    icon_object_event_type_user_subscription_list,
    icon_notification_list, icon_user_object_subscriptions_list
)
from .permissions import (
    permission_events_clear, permission_events_export, permission_events_view
)


def condition_can_be_cleared(context, resolved_object):
    # Hidden import.
    from mayan.apps.acls.classes import ModelPermission
    return permission_events_clear.stored_permission in ModelPermission.get_for_instance(
        instance=context['resolved_object']
    )


def condition_can_be_exported(context, resolved_object):
    # Hidden import.
    from mayan.apps.acls.classes import ModelPermission
    return permission_events_export.stored_permission in ModelPermission.get_for_instance(
        instance=context['resolved_object']
    )


def get_unread_notification_count(context):
    Notification = apps.get_model(
        app_label='events', model_name='Notification'
    )
    if context.request.user.is_authenticated:
        count = Notification.objects.filter(
            user=context.request.user
        ).filter(read=False).count()
        return str(count) if count > 0 else ""


link_event_list = Link(
    icon=icon_event_list, text=_('Events'), view='events:event_list'
)
link_event_list_clear = Link(
    icon=icon_event_list_clear, text=_('Clear events'),
    view='events:event_list_clear'
)
link_event_list_export = Link(
    icon=icon_event_list_export, text=_('Export events'),
    view='events:event_list_export'
)
link_event_type_subscription_list = Link(
    condition=condition_is_current_user,
    icon=icon_event_types_subscriptions_list,
    text=_('Event subscriptions'),
    view='events:event_type_user_subscription_list'
)
link_user_object_subscription_list = Link(
    condition=condition_is_current_user,
    icon=icon_user_object_subscriptions_list,
    text=_('Object event subscriptions'),
    view='events:user_object_subscription_list'
)

link_notification_list = Link(
    badge_text=get_unread_notification_count,
    condition=condition_user_is_authenticated,
    icon=icon_notification_list, text='',
    view='events:user_notifications_list'
)
link_notification_mark_read = Link(
    args='object.pk', icon=icon_notification_mark_read,
    permissions=(permission_events_view,), text=_('Mark as seen'),
    view='events:notification_mark_read'
)
link_notification_mark_read_all = Link(
    icon=icon_notification_mark_read_all, text=_('Mark all as seen'),
    view='events:notification_mark_read_all'
)
link_object_event_list = Link(
    icon=icon_object_event_list,
    kwargs=get_content_type_kwargs_factory(variable_name='resolved_object'),
    permissions=(permission_events_view,), text=_('Events'),
    view='events:object_event_list'
)
link_object_event_list_clear = Link(
    condition=condition_can_be_cleared,
    icon=icon_object_event_list_clear,
    kwargs=get_content_type_kwargs_factory(variable_name='resolved_object'),
    permissions=(permission_events_view,), text=_('Clear events'),
    view='events:object_event_list_clear'
)
link_object_event_list_export = Link(
    condition=condition_can_be_exported,
    icon=icon_object_event_list_export,
    kwargs=get_content_type_kwargs_factory(variable_name='resolved_object'),
    permissions=(permission_events_view,), text=_('Export events'),
    view='events:object_event_list_export'
)
link_object_event_type_user_subscription_list = Link(
    condition=condition_not_is_current_user,
    icon=icon_object_event_type_user_subscription_list,
    kwargs=get_content_type_kwargs_factory(variable_name='resolved_object'),
    permissions=(permission_events_view,), text=_('Subscriptions'),
    view='events:object_event_type_user_subscription_list'
)
