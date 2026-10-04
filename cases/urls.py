from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cases/new/", views.case_new, name="case_new"),
    path("cases/<str:reference>/", views.case_detail, name="case_detail"),
    path("cases/<str:reference>/edit/", views.case_edit, name="case_edit"),
    path("cases/<str:reference>/close/", views.case_close, name="case_close"),
    path("cases/<str:reference>/reopen/", views.case_reopen, name="case_reopen"),
    path("cases/<str:reference>/delete/", views.case_delete, name="case_delete"),
    path("cases/<str:reference>/follow-up/", views.follow_up_set, name="follow_up_set"),
    path("cases/<str:reference>/steps/<int:step_id>/done/", views.step_done, name="step_done"),
    path("cases/<str:reference>/steps/<int:step_id>/skip/", views.step_skip, name="step_skip"),
    path("cases/<str:reference>/steps/<int:step_id>/reopen/", views.step_reopen, name="step_reopen"),
    path("cases/<str:reference>/evidence/add/", views.evidence_add, name="evidence_add"),
    path("cases/<str:reference>/evidence/<int:evidence_id>/file/", views.evidence_file, name="evidence_file"),
    path("cases/<str:reference>/evidence/<int:evidence_id>/delete/", views.evidence_delete, name="evidence_delete"),
    path("cases/<str:reference>/timeline/add/", views.event_add, name="event_add"),
    path("cases/<str:reference>/timeline/<int:event_id>/delete/", views.event_delete, name="event_delete"),
    path("cases/<str:reference>/letters/new/", views.letter_new, name="letter_new"),
    path("cases/<str:reference>/letters/<int:letter_id>/", views.letter_edit, name="letter_edit"),
    path("cases/<str:reference>/letters/<int:letter_id>/print/", views.letter_print, name="letter_print"),
    path("cases/<str:reference>/letters/<int:letter_id>/sent/", views.letter_sent, name="letter_sent"),
    path("cases/<str:reference>/letters/<int:letter_id>/delete/", views.letter_delete, name="letter_delete"),
    path("cases/<str:reference>/bundle/", views.bundle_view, name="bundle_view"),
    path("cases/<str:reference>/bundle.zip", views.bundle_zip, name="bundle_zip"),
]
