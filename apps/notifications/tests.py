from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.notifications.models import Notification

class NotificationSyncTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user(
            username='user_a_test',
            email='user_a@test.cit.edu',
            password='testpassword123',
            role=User.Role.STUDENT
        )
        self.user_b = User.objects.create_user(
            username='user_b_test',
            email='user_b@test.cit.edu',
            password='testpassword123',
            role=User.Role.STUDENT
        )

    def test_scenario_1_no_notifications(self):
        """Scenario 1: No notifications: bell badge hidden/0, inbox displays empty state."""
        self.client.force_login(self.user_a)
        
        # Check unread count API
        res = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], 0)

        # Check notification list view
        list_res = self.client.get(reverse('notifications:list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, 'Your notification inbox is clean and up to date.')
        self.assertContains(list_res, 'id="navNotificationBadge" style="display:none;"')

    def test_scenario_2_three_unread_notifications(self):
        """Scenario 2: Three unread notifications: badge displays 3, inbox shows them."""
        for i in range(1, 4):
            Notification.objects.create(
                user=self.user_a,
                title=f"Alert #{i}",
                message=f"Important message #{i}",
                category=Notification.Category.ACADEMIC_ALERT,
                is_read=False
            )

        self.client.force_login(self.user_a)
        
        # Unread count API
        res = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['count'], 3)

        # List page rendering
        list_res = self.client.get(reverse('notifications:list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, 'Alert #1')
        self.assertContains(list_res, 'Alert #2')
        self.assertContains(list_res, 'Alert #3')
        # Navbar badge should contain '3' and NOT have display:none
        self.assertContains(list_res, 'id="navNotificationBadge" style="">3</span>')

    def test_scenario_3_mark_one_as_read(self):
        """Scenario 3: Mark one notification as read: badge decreases to 2."""
        notifs = []
        for i in range(1, 4):
            notifs.append(Notification.objects.create(
                user=self.user_a,
                title=f"Ticket #{i}",
                message=f"Ticket #{i} updated",
                category=Notification.Category.COMPLAINT_UPDATE,
                is_read=False
            ))

        self.client.force_login(self.user_a)
        target = notifs[0]

        # AJAX POST to mark read
        res = self.client.post(
            reverse('notifications:mark_read', args=[target.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['unread_count'], 2)

        # Verify database record
        target.refresh_from_db()
        self.assertTrue(target.is_read)
        self.assertEqual(Notification.objects.filter(user=self.user_a, is_read=False).count(), 2)

    def test_scenario_4_mark_all_as_read(self):
        """Scenario 4: Mark all as read: badge hides/0, inbox retains read notifications."""
        for i in range(1, 4):
            Notification.objects.create(
                user=self.user_a,
                title=f"Transit Alert #{i}",
                message=f"Bus delay notification #{i}",
                category=Notification.Category.TRANSPORT_ALERT,
                is_read=False
            )

        self.client.force_login(self.user_a)

        # AJAX Mark All Read
        res = self.client.post(
            reverse('notifications:mark_all_read'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_ACCEPT='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['unread_count'], 0)

        # Verify DB: 0 unread, but all 3 still exist as read
        self.assertEqual(Notification.objects.filter(user=self.user_a, is_read=False).count(), 0)
        self.assertEqual(Notification.objects.filter(user=self.user_a, is_read=True).count(), 3)

        # Verify Inbox retains read notifications instead of showing empty state
        list_res = self.client.get(reverse('notifications:list'))
        self.assertEqual(list_res.status_code, 200)
        self.assertContains(list_res, 'Transit Alert #1')
        self.assertContains(list_res, '✓ Read')
        self.assertContains(list_res, 'id="navNotificationBadge" style="display:none;"')

    def test_scenario_5_page_reload_consistency(self):
        """Scenario 5: Reload page: badge and notification list match DB exactly."""
        Notification.objects.create(user=self.user_a, title="Single Alert", is_read=False)
        self.client.force_login(self.user_a)

        res1 = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res1.json()['count'], 1)

        # Simulate page reloads
        res2 = self.client.get(reverse('common:home'))
        self.assertContains(res2, 'id="navNotificationBadge" style="">1</span>')
        
        res3 = self.client.get(reverse('notifications:list'))
        self.assertContains(res3, 'Single Alert')
        self.assertContains(res3, 'id="navNotificationBadge" style="">1</span>')

    def test_scenario_6_receive_new_notification(self):
        """Scenario 6: Receive a new notification: list and badge update immediately."""
        self.client.force_login(self.user_a)
        res_initial = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res_initial.json()['count'], 0)

        # External event generates notification
        Notification.objects.create(
            user=self.user_a,
            title="Real-Time New Alert",
            message="Dynamic notification arrived",
            category=Notification.Category.HOSTEL_ALERT
        )

        res_updated = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res_updated.json()['count'], 1)

        list_res = self.client.get(reverse('notifications:api_list'))
        self.assertEqual(list_res.json()['unread_count'], 1)
        self.assertEqual(list_res.json()['notifications'][0]['title'], 'Real-Time New Alert')

    def test_scenario_7_user_isolation(self):
        """Scenario 7: Switch users: each sees strictly their own notifications, cross-access forbidden."""
        notif_a = Notification.objects.create(user=self.user_a, title="User A Private Alert", is_read=False)
        
        # User B logs in
        self.client.force_login(self.user_b)
        res_b = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res_b.json()['count'], 0)

        list_b = self.client.get(reverse('notifications:list'))
        self.assertNotContains(list_b, 'User A Private Alert')

        # User B attempts to mark User A's notification as read
        cross_res = self.client.post(reverse('notifications:mark_read', args=[notif_a.pk]))
        self.assertEqual(cross_res.status_code, 404)
        notif_a.refresh_from_db()
        self.assertFalse(notif_a.is_read)

    def test_scenario_8_security_unauthenticated(self):
        """Scenario 8: Unauthenticated access strictly redirected to login."""
        self.client.logout()
        res_list = self.client.get(reverse('notifications:list'))
        self.assertEqual(res_list.status_code, 302)

        res_api = self.client.get(reverse('notifications:api_unread_count'))
        self.assertEqual(res_api.status_code, 302)
