"""Root Strawberry schema: merges per-app Query / Mutation types."""

import strawberry
from strawberry.tools import merge_types

from apps.applications.graphql.mutations import StudyRequestsMutation
from apps.applications.graphql.queries import StudyRequestsQuery
from apps.employees.graphql.mutations import HospitalStaffMutation
from apps.employees.graphql.queries import HospitalStaffQuery
from apps.hospital_directory.graphql.mutations import HospitalDirectoryMutation
from apps.hospital_directory.graphql.queries import HospitalDirectoryQuery
from apps.imports.graphql.mutations import ImportsMutation
from apps.imports.graphql.queries import ImportsQuery
from apps.notifications.graphql.mutations import NotificationsMutation
from apps.notifications.graphql.queries import NotificationsQuery
from apps.reports.graphql.queries import ReportsQuery
from apps.students.graphql.mutations import StudentsMutation
from apps.students.graphql.queries import StudentsQuery
from apps.users.graphql.mutations import UsersMutation
from apps.users.graphql.queries import UsersQuery

from graphql_api.core_queries import CoreQuery

Query = merge_types(
    "Query",
    (
        CoreQuery,
        UsersQuery,
        HospitalDirectoryQuery,
        HospitalStaffQuery,
        StudentsQuery,
        StudyRequestsQuery,
        NotificationsQuery,
        ImportsQuery,
        ReportsQuery,
    ),
)

Mutation = merge_types(
    "Mutation",
    (
        UsersMutation,
        HospitalDirectoryMutation,
        HospitalStaffMutation,
        StudentsMutation,
        StudyRequestsMutation,
        ImportsMutation,
        NotificationsMutation,
    ),
)

schema = strawberry.Schema(query=Query, mutation=Mutation)
