--
-- PostgreSQL database dump
--

\restrict x9rnf1kzSPOXB07Pz6aD98iHu9iM8xiD4fVTqkMjFM9Ek92H0mNtkBXOKYCZdLw

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_92473840_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissio_permission_id_6d08dcd2_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_f500bee5_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_group_id_2f3517aa_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.university_departments DROP CONSTRAINT IF EXISTS university_departmen_faculty_id_8b44f025_fk_universit;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_user_id_37ebcf0c_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_supervisor_id_791679ac_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_hospital_department__f9dbbb22_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_faculty_entity_id_6e4aca31_fk_universit;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_department_entity_id_8caabb50_fk_universit;
ALTER TABLE IF EXISTS ONLY public.staff_role_capabilities DROP CONSTRAINT IF EXISTS staff_role_capabilities_role_id_bb650cb4_fk_staff_roles_id;
ALTER TABLE IF EXISTS ONLY public.staff_role_capabilities DROP CONSTRAINT IF EXISTS staff_role_capabilit_capability_id_a264d008_fk_staff_cap;
ALTER TABLE IF EXISTS ONLY public.staff_capability_overrides DROP CONSTRAINT IF EXISTS staff_capability_ove_staff_id_d1b4b15e_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.staff_capability_overrides DROP CONSTRAINT IF EXISTS staff_capability_ove_capability_id_8b2b9b19_fk_staff_cap;
ALTER TABLE IF EXISTS ONLY public.review_trail DROP CONSTRAINT IF EXISTS review_trail_reviewer_id_558887fe_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.review_trail DROP CONSTRAINT IF EXISTS review_trail_application_id_7038db39_fk_applications_id;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_sender_id_57e62d28_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_recipient_id_e1133bac_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_parent_id_2d419239_fk_notifications_id;
ALTER TABLE IF EXISTS ONLY public.import_batches DROP CONSTRAINT IF EXISTS import_batches_imported_by_id_52313233_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS hospital_staff_staff_role_id_e881277e_fk_staff_roles_id;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_working_site_id_8008b9b7_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_user_id_a490e3b4_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_hod_id_fa9a3d13_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_designation_id_c471d8a8_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_department_id_cfac7436_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.department_hod_assignments DROP CONSTRAINT IF EXISTS department_hod_assignments_hod_user_id_b42e6f4c_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.department_hod_assignments DROP CONSTRAINT IF EXISTS department_hod_assig_department_id_9ea9ed14_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.applications DROP CONSTRAINT IF EXISTS applications_hospital_department__af1d18c6_fk_hospital_;
ALTER TABLE IF EXISTS ONLY public.applications DROP CONSTRAINT IF EXISTS applications_applicant_id_0f5ee165_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.application_documents DROP CONSTRAINT IF EXISTS application_document_application_id_fe7e9522_fk_applicati;
ALTER TABLE IF EXISTS ONLY public.application_change_requests DROP CONSTRAINT IF EXISTS application_change_requests_sender_id_914f3b80_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.application_change_requests DROP CONSTRAINT IF EXISTS application_change_r_application_id_3c947242_fk_applicati;
DROP INDEX IF EXISTS public.users_username_e8658fc8_like;
DROP INDEX IF EXISTS public.users_user_permissions_user_id_92473840;
DROP INDEX IF EXISTS public.users_user_permissions_permission_id_6d08dcd2;
DROP INDEX IF EXISTS public.users_groups_user_id_f500bee5;
DROP INDEX IF EXISTS public.users_groups_group_id_2f3517aa;
DROP INDEX IF EXISTS public.university_faculties_name_c116fa31_like;
DROP INDEX IF EXISTS public.university_departments_faculty_id_8b44f025;
DROP INDEX IF EXISTS public.student_profiles_supervisor_id_791679ac;
DROP INDEX IF EXISTS public.student_profiles_registration_no_57b0f01d_like;
DROP INDEX IF EXISTS public.student_profiles_hospital_department_id_f9dbbb22;
DROP INDEX IF EXISTS public.student_profiles_faculty_entity_id_6e4aca31;
DROP INDEX IF EXISTS public.student_profiles_department_entity_id_8caabb50;
DROP INDEX IF EXISTS public.staff_roles_code_840f7694_like;
DROP INDEX IF EXISTS public.staff_role_capabilities_role_id_bb650cb4;
DROP INDEX IF EXISTS public.staff_role_capabilities_capability_id_a264d008;
DROP INDEX IF EXISTS public.staff_capability_overrides_staff_id_d1b4b15e;
DROP INDEX IF EXISTS public.staff_capability_overrides_capability_id_8b2b9b19;
DROP INDEX IF EXISTS public.staff_capabilities_catalog_code_30e6dd85_like;
DROP INDEX IF EXISTS public.review_trail_reviewer_id_558887fe;
DROP INDEX IF EXISTS public.review_trail_application_id_7038db39;
DROP INDEX IF EXISTS public.notifications_sender_id_57e62d28;
DROP INDEX IF EXISTS public.notifications_recipient_id_e1133bac;
DROP INDEX IF EXISTS public.notifications_parent_id_2d419239;
DROP INDEX IF EXISTS public.notificatio_recipie_583549_idx;
DROP INDEX IF EXISTS public.notif_parent_idx;
DROP INDEX IF EXISTS public.import_batches_imported_by_id_52313233;
DROP INDEX IF EXISTS public.hospital_working_sites_name_3fa72660_like;
DROP INDEX IF EXISTS public.hospital_staff_staff_role_id_e881277e;
DROP INDEX IF EXISTS public.hospital_sponsorship_types_name_81028ee0_like;
DROP INDEX IF EXISTS public.hospital_designations_name_dd566948_like;
DROP INDEX IF EXISTS public.hospital_departments_name_61beb336_like;
DROP INDEX IF EXISTS public.hospital_application_document_kinds_code_877f0888_like;
DROP INDEX IF EXISTS public.employee_profiles_working_site_id_8008b9b7;
DROP INDEX IF EXISTS public.employee_profiles_hod_id_fa9a3d13;
DROP INDEX IF EXISTS public.employee_profiles_employee_number_6b982a33_like;
DROP INDEX IF EXISTS public.employee_profiles_designation_id_c471d8a8;
DROP INDEX IF EXISTS public.employee_profiles_department_id_cfac7436;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.department_hod_assignments_hod_user_id_b42e6f4c;
DROP INDEX IF EXISTS public.department_hod_assignments_department_id_9ea9ed14;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
DROP INDEX IF EXISTS public.applications_hospital_department_id_af1d18c6;
DROP INDEX IF EXISTS public.applications_applicant_id_0f5ee165;
DROP INDEX IF EXISTS public.applications_app_ref_52ca47a8_like;
DROP INDEX IF EXISTS public.application_status_f8f5ce_idx;
DROP INDEX IF EXISTS public.application_documents_application_id_fe7e9522;
DROP INDEX IF EXISTS public.application_change_requests_sender_id_914f3b80;
DROP INDEX IF EXISTS public.application_change_requests_application_id_3c947242;
DROP INDEX IF EXISTS public.application_applica_e9ee09_idx;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_username_key;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_permission_id_3b86cbdf_uniq;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_group_id_fc7788e8_uniq;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.university_faculties DROP CONSTRAINT IF EXISTS university_faculties_pkey;
ALTER TABLE IF EXISTS ONLY public.university_faculties DROP CONSTRAINT IF EXISTS university_faculties_name_key;
ALTER TABLE IF EXISTS ONLY public.university_departments DROP CONSTRAINT IF EXISTS university_departments_pkey;
ALTER TABLE IF EXISTS ONLY public.university_departments DROP CONSTRAINT IF EXISTS uniq_university_department_per_faculty;
ALTER TABLE IF EXISTS ONLY public.staff_role_capabilities DROP CONSTRAINT IF EXISTS uniq_staff_role_capability;
ALTER TABLE IF EXISTS ONLY public.staff_capability_overrides DROP CONSTRAINT IF EXISTS uniq_staff_capability_override;
ALTER TABLE IF EXISTS ONLY public.department_hod_assignments DROP CONSTRAINT IF EXISTS uniq_department_hod_assignment;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_registration_no_key;
ALTER TABLE IF EXISTS ONLY public.student_profiles DROP CONSTRAINT IF EXISTS student_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.staff_roles DROP CONSTRAINT IF EXISTS staff_roles_pkey;
ALTER TABLE IF EXISTS ONLY public.staff_roles DROP CONSTRAINT IF EXISTS staff_roles_code_key;
ALTER TABLE IF EXISTS ONLY public.staff_role_capabilities DROP CONSTRAINT IF EXISTS staff_role_capabilities_pkey;
ALTER TABLE IF EXISTS ONLY public.staff_capability_overrides DROP CONSTRAINT IF EXISTS staff_capability_overrides_pkey;
ALTER TABLE IF EXISTS ONLY public.staff_capabilities_catalog DROP CONSTRAINT IF EXISTS staff_capabilities_catalog_pkey;
ALTER TABLE IF EXISTS ONLY public.staff_capabilities_catalog DROP CONSTRAINT IF EXISTS staff_capabilities_catalog_code_key;
ALTER TABLE IF EXISTS ONLY public.review_trail DROP CONSTRAINT IF EXISTS review_trail_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.import_batches DROP CONSTRAINT IF EXISTS import_batches_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_working_sites DROP CONSTRAINT IF EXISTS hospital_working_sites_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_working_sites DROP CONSTRAINT IF EXISTS hospital_working_sites_name_key;
ALTER TABLE IF EXISTS ONLY public.hospital_sponsorship_types DROP CONSTRAINT IF EXISTS hospital_sponsorship_types_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_sponsorship_types DROP CONSTRAINT IF EXISTS hospital_sponsorship_types_name_key;
ALTER TABLE IF EXISTS ONLY public.hospital_designations DROP CONSTRAINT IF EXISTS hospital_designations_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_designations DROP CONSTRAINT IF EXISTS hospital_designations_name_key;
ALTER TABLE IF EXISTS ONLY public.hospital_departments DROP CONSTRAINT IF EXISTS hospital_departments_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_departments DROP CONSTRAINT IF EXISTS hospital_departments_name_key;
ALTER TABLE IF EXISTS ONLY public.hospital_application_document_kinds DROP CONSTRAINT IF EXISTS hospital_application_document_kinds_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_application_document_kinds DROP CONSTRAINT IF EXISTS hospital_application_document_kinds_code_key;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.hospital_staff DROP CONSTRAINT IF EXISTS employee_profiles_employee_number_key;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.department_hod_assignments DROP CONSTRAINT IF EXISTS department_hod_assignments_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
ALTER TABLE IF EXISTS ONLY public.applications DROP CONSTRAINT IF EXISTS applications_pkey;
ALTER TABLE IF EXISTS ONLY public.applications DROP CONSTRAINT IF EXISTS applications_app_ref_key;
ALTER TABLE IF EXISTS ONLY public.application_documents DROP CONSTRAINT IF EXISTS application_documents_pkey;
ALTER TABLE IF EXISTS ONLY public.application_change_requests DROP CONSTRAINT IF EXISTS application_change_requests_pkey;
DROP TABLE IF EXISTS public.users_user_permissions;
DROP TABLE IF EXISTS public.users_groups;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.university_faculties;
DROP TABLE IF EXISTS public.university_departments;
DROP TABLE IF EXISTS public.student_profiles;
DROP TABLE IF EXISTS public.staff_roles;
DROP TABLE IF EXISTS public.staff_role_capabilities;
DROP TABLE IF EXISTS public.staff_capability_overrides;
DROP TABLE IF EXISTS public.staff_capabilities_catalog;
DROP TABLE IF EXISTS public.review_trail;
DROP TABLE IF EXISTS public.notifications;
DROP TABLE IF EXISTS public.import_batches;
DROP TABLE IF EXISTS public.hospital_working_sites;
DROP TABLE IF EXISTS public.hospital_staff;
DROP TABLE IF EXISTS public.hospital_sponsorship_types;
DROP TABLE IF EXISTS public.hospital_designations;
DROP TABLE IF EXISTS public.hospital_departments;
DROP TABLE IF EXISTS public.hospital_application_document_kinds;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.department_hod_assignments;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
DROP TABLE IF EXISTS public.applications;
DROP TABLE IF EXISTS public.application_documents;
DROP TABLE IF EXISTS public.application_change_requests;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: application_change_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.application_change_requests (
    id uuid NOT NULL,
    target character varying(20) NOT NULL,
    message text NOT NULL,
    reply_contact_email character varying(254) NOT NULL,
    notify_via_system boolean NOT NULL,
    notify_via_email boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    application_id uuid NOT NULL,
    sender_id uuid NOT NULL
);


--
-- Name: application_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.application_documents (
    id uuid NOT NULL,
    doc_type character varying(100) NOT NULL,
    file character varying(255) NOT NULL,
    uploaded_at timestamp with time zone NOT NULL,
    application_id uuid NOT NULL
);


--
-- Name: applications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.applications (
    id uuid NOT NULL,
    app_ref character varying(30),
    app_type character varying(30) NOT NULL,
    status character varying(30) NOT NULL,
    current_stage character varying(50) NOT NULL,
    submitted_at timestamp with time zone,
    updated_at timestamp with time zone NOT NULL,
    institution_name character varying(200) NOT NULL,
    programme_applied character varying(200) NOT NULL,
    start_date date,
    end_date date,
    sponsorship_type character varying(100) NOT NULL,
    reason_for_study text NOT NULL,
    attachment_dept character varying(100) NOT NULL,
    attachment_start date,
    attachment_end date,
    supervisor_requested character varying(100) NOT NULL,
    applicant_id uuid NOT NULL,
    hospital_department_id uuid,
    placement_scope character varying(20) NOT NULL,
    field_records_shared_at timestamp with time zone,
    hr_feedback_for_university text NOT NULL,
    placement_conducted_site character varying(400) NOT NULL
);


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: department_hod_assignments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.department_hod_assignments (
    id uuid NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    department_id uuid NOT NULL,
    hod_user_id uuid NOT NULL
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id uuid NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: hospital_application_document_kinds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital_application_document_kinds (
    id uuid NOT NULL,
    code character varying(80) NOT NULL,
    label character varying(200) NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT hospital_application_document_kinds_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: hospital_departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital_departments (
    id uuid NOT NULL,
    name character varying(200) NOT NULL,
    code character varying(50) NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT hospital_departments_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: hospital_designations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital_designations (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT hospital_designations_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: hospital_sponsorship_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital_sponsorship_types (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT hospital_sponsorship_types_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: hospital_staff; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital_staff (
    id uuid CONSTRAINT employee_profiles_id_not_null NOT NULL,
    staff_number character varying(30) CONSTRAINT employee_profiles_employee_number_not_null NOT NULL,
    full_name character varying(100) CONSTRAINT employee_profiles_full_name_not_null NOT NULL,
    phone character varying(20) CONSTRAINT employee_profiles_phone_not_null NOT NULL,
    national_id character varying(50) CONSTRAINT employee_profiles_national_id_not_null NOT NULL,
    date_employed date CONSTRAINT employee_profiles_date_employed_not_null NOT NULL,
    hod_id uuid,
    user_id uuid CONSTRAINT employee_profiles_user_id_not_null NOT NULL,
    department_id uuid,
    designation_id uuid,
    working_site_id uuid,
    capabilities jsonb NOT NULL,
    staff_role_id uuid
);


--
-- Name: hospital_working_sites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hospital_working_sites (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT hospital_working_sites_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: import_batches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.import_batches (
    id uuid NOT NULL,
    batch_type character varying(20) NOT NULL,
    file_name character varying(255) NOT NULL,
    total_rows integer NOT NULL,
    success_rows integer NOT NULL,
    failed_rows integer NOT NULL,
    status character varying(30) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    imported_by_id uuid NOT NULL,
    CONSTRAINT import_batches_failed_rows_check CHECK ((failed_rows >= 0)),
    CONSTRAINT import_batches_success_rows_check CHECK ((success_rows >= 0)),
    CONSTRAINT import_batches_total_rows_check CHECK ((total_rows >= 0))
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id uuid NOT NULL,
    message text NOT NULL,
    is_read boolean NOT NULL,
    notif_type character varying(50) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    recipient_id uuid NOT NULL,
    destination_path character varying(255) NOT NULL,
    sender_id uuid,
    parent_id uuid
);


--
-- Name: review_trail; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.review_trail (
    id uuid NOT NULL,
    stage character varying(50) NOT NULL,
    decision character varying(20) NOT NULL,
    remarks text NOT NULL,
    reviewed_at timestamp with time zone NOT NULL,
    application_id uuid NOT NULL,
    reviewer_id uuid NOT NULL,
    letter_body text NOT NULL,
    signature_data text NOT NULL,
    feedback_target character varying(20) NOT NULL
);


--
-- Name: staff_capabilities_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staff_capabilities_catalog (
    id uuid NOT NULL,
    code character varying(80) NOT NULL,
    label character varying(180) NOT NULL,
    description text NOT NULL,
    module character varying(80) NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT staff_capabilities_catalog_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: staff_capability_overrides; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staff_capability_overrides (
    id uuid NOT NULL,
    mode character varying(10) NOT NULL,
    is_active boolean NOT NULL,
    capability_id uuid NOT NULL,
    staff_id uuid NOT NULL
);


--
-- Name: staff_role_capabilities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staff_role_capabilities (
    id uuid NOT NULL,
    is_active boolean NOT NULL,
    capability_id uuid NOT NULL,
    role_id uuid NOT NULL
);


--
-- Name: staff_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.staff_roles (
    id uuid NOT NULL,
    code character varying(60) NOT NULL,
    name character varying(120) NOT NULL,
    description text NOT NULL,
    is_active boolean NOT NULL,
    sort_order smallint NOT NULL,
    CONSTRAINT staff_roles_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: student_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.student_profiles (
    id uuid NOT NULL,
    registration_no character varying(30) NOT NULL,
    full_name character varying(100) NOT NULL,
    programme character varying(100) NOT NULL,
    faculty character varying(100) NOT NULL,
    year_of_study smallint NOT NULL,
    phone character varying(20) NOT NULL,
    dob character varying(20) NOT NULL,
    university character varying(100) NOT NULL,
    supervisor_id uuid,
    user_id uuid NOT NULL,
    contact_email character varying(254) NOT NULL,
    dashboard_notes text NOT NULL,
    gender character varying(20) NOT NULL,
    hospital_department_id uuid,
    level_of_study character varying(30) NOT NULL,
    department_entity_id uuid,
    faculty_entity_id uuid,
    CONSTRAINT student_profiles_year_of_study_check CHECK ((year_of_study >= 0))
);


--
-- Name: university_departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.university_departments (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    sort_order smallint NOT NULL,
    faculty_id uuid NOT NULL,
    is_active boolean NOT NULL,
    CONSTRAINT university_departments_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: university_faculties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.university_faculties (
    id uuid NOT NULL,
    name character varying(150) NOT NULL,
    sort_order smallint NOT NULL,
    is_active boolean NOT NULL,
    CONSTRAINT university_faculties_sort_order_check CHECK ((sort_order >= 0))
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    id uuid NOT NULL,
    username character varying(50) NOT NULL,
    role character varying(30) NOT NULL,
    module character varying(30) NOT NULL,
    is_first_login boolean NOT NULL,
    created_at timestamp with time zone NOT NULL
);


--
-- Name: users_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_groups (
    id bigint NOT NULL,
    user_id uuid NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: users_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_user_permissions (
    id bigint NOT NULL,
    user_id uuid NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: application_change_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.application_change_requests (id, target, message, reply_contact_email, notify_via_system, notify_via_email, created_at, application_id, sender_id) FROM stdin;
\.


--
-- Data for Name: application_documents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.application_documents (id, doc_type, file, uploaded_at, application_id) FROM stdin;
\.


--
-- Data for Name: applications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.applications (id, app_ref, app_type, status, current_stage, submitted_at, updated_at, institution_name, programme_applied, start_date, end_date, sponsorship_type, reason_for_study, attachment_dept, attachment_start, attachment_end, supervisor_requested, applicant_id, hospital_department_id, placement_scope, field_records_shared_at, hr_feedback_for_university, placement_conducted_site) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	3	add_permission
6	Can change permission	3	change_permission
7	Can delete permission	3	delete_permission
8	Can view permission	3	view_permission
9	Can add group	2	add_group
10	Can change group	2	change_group
11	Can delete group	2	delete_group
12	Can view group	2	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add user	6	add_user
22	Can change user	6	change_user
23	Can delete user	6	delete_user
24	Can view user	6	view_user
25	Can add department	8	add_department
26	Can change department	8	change_department
27	Can delete department	8	delete_department
28	Can view department	8	view_department
29	Can add designation	9	add_designation
30	Can change designation	9	change_designation
31	Can delete designation	9	delete_designation
32	Can view designation	9	view_designation
33	Can add working site	11	add_workingsite
34	Can change working site	11	change_workingsite
35	Can delete working site	11	delete_workingsite
36	Can view working site	11	view_workingsite
37	Can add application document kind	7	add_applicationdocumentkind
38	Can change application document kind	7	change_applicationdocumentkind
39	Can delete application document kind	7	delete_applicationdocumentkind
40	Can view application document kind	7	view_applicationdocumentkind
41	Can add sponsorship type	10	add_sponsorshiptype
42	Can change sponsorship type	10	change_sponsorshiptype
43	Can delete sponsorship type	10	delete_sponsorshiptype
44	Can view sponsorship type	10	view_sponsorshiptype
45	Can add hospital staff	13	add_hospitalstaff
46	Can change hospital staff	13	change_hospitalstaff
47	Can delete hospital staff	13	delete_hospitalstaff
48	Can view hospital staff	13	view_hospitalstaff
49	Can add staff capability	14	add_staffcapability
50	Can change staff capability	14	change_staffcapability
51	Can delete staff capability	14	delete_staffcapability
52	Can view staff capability	14	view_staffcapability
53	Can add staff role	16	add_staffrole
54	Can change staff role	16	change_staffrole
55	Can delete staff role	16	delete_staffrole
56	Can view staff role	16	view_staffrole
57	Can add staff capability override	15	add_staffcapabilityoverride
58	Can change staff capability override	15	change_staffcapabilityoverride
59	Can delete staff capability override	15	delete_staffcapabilityoverride
60	Can view staff capability override	15	view_staffcapabilityoverride
61	Can add staff role capability	17	add_staffrolecapability
62	Can change staff role capability	17	change_staffrolecapability
63	Can delete staff role capability	17	delete_staffrolecapability
64	Can view staff role capability	17	view_staffrolecapability
65	Can add department hod assignment	12	add_departmenthodassignment
66	Can change department hod assignment	12	change_departmenthodassignment
67	Can delete department hod assignment	12	delete_departmenthodassignment
68	Can view department hod assignment	12	view_departmenthodassignment
69	Can add student profile	18	add_studentprofile
70	Can change student profile	18	change_studentprofile
71	Can delete student profile	18	delete_studentprofile
72	Can view student profile	18	view_studentprofile
73	Can add university department	19	add_universitydepartment
74	Can change university department	19	change_universitydepartment
75	Can delete university department	19	delete_universitydepartment
76	Can view university department	19	view_universitydepartment
77	Can add university faculty	20	add_universityfaculty
78	Can change university faculty	20	change_universityfaculty
79	Can delete university faculty	20	delete_universityfaculty
80	Can view university faculty	20	view_universityfaculty
81	Can add study or attachment request	21	add_application
82	Can change study or attachment request	21	change_application
83	Can delete study or attachment request	21	delete_application
84	Can view study or attachment request	21	view_application
85	Can add request document	22	add_applicationdocument
86	Can change request document	22	change_applicationdocument
87	Can delete request document	22	delete_applicationdocument
88	Can view request document	22	view_applicationdocument
89	Can add request review entry	24	add_reviewtrail
90	Can change request review entry	24	change_reviewtrail
91	Can delete request review entry	24	delete_reviewtrail
92	Can view request review entry	24	view_reviewtrail
93	Can add change request	23	add_changerequest
94	Can change change request	23	change_changerequest
95	Can delete change request	23	delete_changerequest
96	Can view change request	23	view_changerequest
97	Can add notification	25	add_notification
98	Can change notification	25	change_notification
99	Can delete notification	25	delete_notification
100	Can view notification	25	view_notification
101	Can add import batch	26	add_importbatch
102	Can change import batch	26	change_importbatch
103	Can delete import batch	26	delete_importbatch
104	Can view import batch	26	view_importbatch
\.


--
-- Data for Name: department_hod_assignments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.department_hod_assignments (id, is_active, created_at, updated_at, department_id, hod_user_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	contenttypes	contenttype
5	sessions	session
6	users	user
7	hospital_directory	applicationdocumentkind
8	hospital_directory	department
9	hospital_directory	designation
10	hospital_directory	sponsorshiptype
11	hospital_directory	workingsite
12	employees	departmenthodassignment
13	employees	hospitalstaff
14	employees	staffcapability
15	employees	staffcapabilityoverride
16	employees	staffrole
17	employees	staffrolecapability
18	students	studentprofile
19	students	universitydepartment
20	students	universityfaculty
21	applications	application
22	applications	applicationdocument
23	applications	changerequest
24	applications	reviewtrail
25	notifications	notification
26	imports	importbatch
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-06-20 19:00:09.175708+03
2	contenttypes	0002_remove_content_type_name	2026-06-20 19:00:09.188398+03
3	auth	0001_initial	2026-06-20 19:00:09.255855+03
4	auth	0002_alter_permission_name_max_length	2026-06-20 19:00:09.266745+03
5	auth	0003_alter_user_email_max_length	2026-06-20 19:00:09.27227+03
6	auth	0004_alter_user_username_opts	2026-06-20 19:00:09.277681+03
7	auth	0005_alter_user_last_login_null	2026-06-20 19:00:09.285834+03
8	auth	0006_require_contenttypes_0002	2026-06-20 19:00:09.287326+03
9	auth	0007_alter_validators_add_error_messages	2026-06-20 19:00:09.297079+03
10	auth	0008_alter_user_username_max_length	2026-06-20 19:00:09.305944+03
11	auth	0009_alter_user_last_name_max_length	2026-06-20 19:00:09.313241+03
12	auth	0010_alter_group_name_max_length	2026-06-20 19:00:09.325395+03
13	auth	0011_update_proxy_permissions	2026-06-20 19:00:09.331885+03
14	auth	0012_alter_user_first_name_max_length	2026-06-20 19:00:09.341843+03
15	users	0001_initial	2026-06-20 19:00:09.399362+03
16	admin	0001_initial	2026-06-20 19:00:09.426334+03
17	admin	0002_logentry_remove_auto_add	2026-06-20 19:00:09.437234+03
18	admin	0003_logentry_add_action_flag_choices	2026-06-20 19:00:09.445247+03
19	hospital_directory	0001_initial	2026-06-20 19:00:09.478262+03
20	applications	0001_initial	2026-06-20 19:00:09.504714+03
21	applications	0002_initial	2026-06-20 19:00:09.592628+03
22	applications	0003_application_hospital_department_and_more	2026-06-20 19:00:09.649217+03
23	applications	0004_alter_application_verbose_names	2026-06-20 19:00:09.690392+03
24	applications	0005_attachment_hr_placement_fields	2026-06-20 19:00:09.731458+03
25	applications	0006_attachment_queue_use_hr_stage	2026-06-20 19:00:09.752776+03
26	applications	0007_registry_and_university_extensions	2026-06-20 19:00:09.782646+03
27	applications	0008_add_change_request_model	2026-06-20 19:00:09.813298+03
28	applications	0009_change_request_internal_targets	2026-06-20 19:00:09.83786+03
29	applications	0010_reviewtrail_feedback_target	2026-06-20 19:00:09.869938+03
30	employees	0001_initial	2026-06-20 19:00:09.889011+03
31	employees	0002_initial	2026-06-20 19:00:09.959586+03
32	employees	0003_alter_employeeprofile_department_and_more	2026-06-20 19:00:10.303026+03
33	employees	0004_hospital_staff_and_roles	2026-06-20 19:00:10.514094+03
34	employees	0005_rename_employee_number_to_staff_number	2026-06-20 19:00:10.530225+03
35	employees	0006_hospitalstaff_capabilities	2026-06-20 19:00:10.56905+03
36	employees	0007_staffcapability_staffrole_and_more	2026-06-20 19:00:10.758581+03
37	employees	0008_departmenthodassignment	2026-06-20 19:00:10.81128+03
38	hospital_directory	0002_registry_and_university_extensions	2026-06-20 19:00:10.83421+03
39	hospital_directory	0003_seed_default_catalog	2026-06-20 19:00:10.898599+03
40	imports	0001_initial	2026-06-20 19:00:10.907062+03
41	imports	0002_initial	2026-06-20 19:00:10.944873+03
42	imports	0003_hospital_staff_and_roles	2026-06-20 19:00:11.001967+03
43	notifications	0001_initial	2026-06-20 19:00:11.010417+03
44	notifications	0002_initial	2026-06-20 19:00:11.067892+03
45	notifications	0003_notification_destination_path	2026-06-20 19:00:11.089941+03
46	notifications	0004_notification_sender	2026-06-20 19:00:11.129766+03
47	notifications	0005_notification_parent	2026-06-20 19:00:11.197318+03
48	sessions	0001_initial	2026-06-20 19:00:11.209875+03
49	students	0001_initial	2026-06-20 19:00:11.225331+03
50	students	0002_initial	2026-06-20 19:00:11.29395+03
51	students	0003_studentprofile_contact_email_and_more	2026-06-20 19:00:11.403018+03
52	students	0004_registry_and_university_extensions	2026-06-20 19:00:11.557081+03
53	students	0005_universitydepartment_is_active_and_more	2026-06-20 19:00:11.569666+03
54	users	0002_alter_user_role	2026-06-20 19:00:11.601465+03
55	users	0003_hospital_staff_and_roles	2026-06-20 19:00:11.662864+03
56	users	0004_rename_employee_role_to_hospital_staff	2026-06-20 19:00:11.724942+03
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: hospital_application_document_kinds; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hospital_application_document_kinds (id, code, label, is_active, sort_order) FROM stdin;
10dfa275-85d0-4852-ad33-25d575995141	supporting_letter	Supporting letter	t	0
ab2eb38e-2b10-4b51-9f09-29642d4892c8	id_copy	ID copy	t	1
2d471cb7-972e-48b8-b3ba-a3f2f08ebc73	cv	CV / resume	t	2
7598ac30-0f3f-4908-ac8d-a5d9c5613be5	academic	Academic record	t	3
143fc857-c9c4-4937-a277-a66d096480d4	admission_letter	University admission letter	t	4
a0a6ef92-30db-4f52-86ea-9af2d3dcd25b	other	Other	t	99
\.


--
-- Data for Name: hospital_departments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hospital_departments (id, name, code, is_active, sort_order) FROM stdin;
674e45f3-0e8d-4e14-9e7a-fecfe0930383	Dentist Department	DDPT	t	0
2277e698-8ad4-4f5e-95d9-4ac5b42bcd72	Pharmacy department	PDPT	t	1
00865003-caa8-45d7-b6f8-c80361080391	Physchology Department	PDPT	t	2
31398ab6-a69c-49ce-8466-402d802b3004	Nurse department	NDPT	t	3
cc09a518-07b6-4007-80ae-912011e159dd	MD department	MDEPT	t	4
\.


--
-- Data for Name: hospital_designations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hospital_designations (id, name, is_active, sort_order) FROM stdin;
3fcb0db5-301e-4477-960c-a954a797775a	pharmacist	t	1
a3f6a083-dfa5-42f4-aba3-27164f57aa33	Dentist	t	2
64b18165-c53e-419e-a3d4-4212b27b28ed	Medical Doctor	t	3
6e51d86a-db62-4915-b9b4-f86c41a76c3f	Phychologist	t	4
9a6c560f-2442-4ab8-a4c6-5eaa2b433b94	Nurse	t	0
\.


--
-- Data for Name: hospital_sponsorship_types; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hospital_sponsorship_types (id, name, is_active, sort_order) FROM stdin;
1761164b-93f8-495c-a279-912c5a6b4c3c	Government scholarship	t	0
bfba1473-856f-4b44-abdb-45b6fcf2471c	Self-sponsored	t	1
66a82ba8-839d-443b-a3d4-65e328f71486	Hospital sponsorship	t	2
a8cff279-783c-4909-b617-d0b1c062c59c	NGO / donor funded	t	3
\.


--
-- Data for Name: hospital_staff; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hospital_staff (id, staff_number, full_name, phone, national_id, date_employed, hod_id, user_id, department_id, designation_id, working_site_id, capabilities, staff_role_id) FROM stdin;
\.


--
-- Data for Name: hospital_working_sites; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hospital_working_sites (id, name, is_active, sort_order) FROM stdin;
64fcaebb-4456-425f-a35b-308350cf8ace	Regional Clinic	t	1
ec6a4b2d-754f-47ee-b475-50cad3fe1aa6	Main Hospital Campus	t	0
5c6ac37a-420b-40d9-b5f7-ed05421085db	Mnazi mmoja	t	2
2b6c03f7-1b08-4569-a0c2-d809c36cf7d7	Lumumba Hospital	t	3
\.


--
-- Data for Name: import_batches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.import_batches (id, batch_type, file_name, total_rows, success_rows, failed_rows, status, created_at, imported_by_id) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, message, is_read, notif_type, created_at, recipient_id, destination_path, sender_id, parent_id) FROM stdin;
\.


--
-- Data for Name: review_trail; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.review_trail (id, stage, decision, remarks, reviewed_at, application_id, reviewer_id, letter_body, signature_data, feedback_target) FROM stdin;
\.


--
-- Data for Name: staff_capabilities_catalog; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staff_capabilities_catalog (id, code, label, description, module, is_active, sort_order) FROM stdin;
97d22843-a3a0-4d5e-804a-7529de6b51fc	fs_create	Create New Application	Submit a new further studies application	further_studies	t	4
cba3c5c0-f53e-4752-90e5-22fb10a22f72	fs_existing	Existing application	Resume, edit, or view a draft / submitted application	further_studies	t	0
23edc211-4d96-4b95-8333-0e3203069ab2	fs_edit	Edit Application	Edit draft or returned applications	further_studies	t	1
2ec246a7-d712-4321-8bc2-202cc850665f	fs_delete	Delete Application	Delete own applications	further_studies	t	2
733e5d5d-d6bb-45fe-976a-58ffc654e56d	fs_cancel	Cancel / Withdraw Application	Withdraw applications from the review pipeline	further_studies	t	3
2cd94bfc-2011-42bc-bdd6-55524772bbe4	fs_view_all	View All Applications	Access the full application list	further_studies	f	0
893ef79e-cb6e-4542-9b5f-59d8eb56dc3a	track_notices	Application tracking notices	System messages about application status changes	app_tracking	t	10
9f0e5203-5039-4398-b444-82439e72e174	track_progress	Track application review progress	Visual stage tracker: HoD to assistant director to top management	app_tracking	t	11
24af9228-9469-462c-bae6-a4fbd9e679ca	fb_final_report	View final feedback report	Final acceptance / rejection letter with all three e-signatures (downloadable)	app_feedback	t	21
508afb8f-4081-42cb-80f6-276e76a145a1	fb_hod_report	Final report from HOD	View HOD stage review letters for own applications	app_feedback	t	22
43071674-f035-49c3-8c5b-26af09735ac4	fb_hod_changes	Change requests from head of department	View and act on rectification requests sent by the head of department	staff_change_request	t	20
533cc3b2-f242-41a9-8b2a-bd046663e736	notif_view	View notifications	View all incoming system notifications	notifications	t	30
49d5b3db-fc83-475b-8094-02e4487a551e	notif_send	Send messages	Compose and send in-system messages	notifications	t	31
871d71fc-4abd-4122-b70d-20410e250786	notif_reply	Reply to messages	Reply to received in-system messages	notifications	t	32
3a4a75ec-6b9c-4d56-b428-43b0e0091906	hod_assess_details	Assess application details	Read and assess the staff further studies application	hod_review	t	100
7c402bc6-2765-4a6e-8a38-bfd39316695b	hod_review_doc	Review application document	Open and review attached application documents	hod_review	t	101
6ef928d7-0fc0-40f8-9e9f-8f7e0320523f	hod_send_changes	Send change requests to staff	Request rectification of application details from the staff member	hod_review	t	102
d02107f2-8cf5-40c7-88c6-ae65f0ee90fc	hod_view_department_staff	View department staff (read-only)	View names of staff belonging to assigned department mappings	hod_review	t	103
ec2237a3-6f2f-4d74-8791-a85d7b93a485	hod_create_feedback	Create review feedback	Use the review-feedback template and apply HoD e-signature	hod_send_feedback	t	110
bf9c1f07-b8cb-46f8-bce5-81020ee5e667	hod_send_to_adr	Send review feedback to assistant director	Forward the signed HoD review to the assistant director	hod_send_feedback	t	111
edf47faf-4c30-4463-aedd-76530101e6b1	hod_accept_adr_req	Accept change request from assistant director and respond	Receive and act on a change request sent down from the assistant director	hod_send_feedback	t	112
3256842d-a34d-4a5d-9ada-ceefca922665	hod_view_hr_approved	View field-requests approved students	Read-only view of approved student handoff list from HR	hod_field_requests	t	120
49b5ff51-86b0-4c7c-89a1-275fb943d473	hod_view_final_letter	View approval or rejection letter from top management	Downloadable final letter carrying all three e-signatures	hod_final_feedback	t	130
2d70dc6c-6d45-4048-be03-eea032902624	hod_hub_app_review	Application review	Review staff applications as the first review stage via the HOD workspace	hod_hub_review	t	600
ba427a9d-1b91-4b50-80f7-432b8625dfe3	hod_hub_cr_send	Send Change Request	Send a change request to the Staff applicant	hod_hub_change_request	t	610
bf505455-f7a7-4ec5-9050-e5008f269806	hod_hub_cr_view	View Change Requests	View change requests sent to Staff and received from the Assistant Director	hod_hub_change_request	t	611
960c9535-e84b-44f8-8564-a4868c27cadd	hod_hub_fb_send	Send Review Feedback	Compose and send a signed HOD review feedback to the Assistant Director	hod_hub_review_feedback	t	620
5ed6f5e9-6dfd-47cb-a225-a5dfa4987628	hod_hub_fb_reports	Final Application Reports	View finalised application reports forwarded from the Assistant Director	hod_hub_review_feedback	t	621
aa9880a7-92fe-41ab-b0d6-38d49fcaa33a	adr_assess_details	Assess application details	Read and assess the staff further studies application	adr_review	t	200
93a6d4ab-e42c-4a14-8baa-f4475872f0bf	adr_review_doc	Review application document	Open and review attached application documents	adr_review	t	201
1e82ef2c-29ed-4097-8b76-b64ac160f433	adr_review_hod_fb	Review head of department review feedback	Read the review feedback submitted by the head of department	adr_review	t	202
2e847566-f52e-46b8-8d90-e2c54037918f	adr_send_changes	Send change requests to head of department	Request amendments from the head of department	adr_review	t	203
9a6e5819-dc2d-42c4-bdd6-98d839b3b88e	adr_create_feedback	Create review feedback	Use the review-feedback template and apply assistant director e-signature	adr_send_feedback	t	210
c77f55ca-1b93-45bc-ad8e-97c80d3036f5	adr_send_to_top	Send review feedback to top management	Forward the signed ADR review to top management	adr_send_feedback	t	211
7b0c20a9-48ea-4ad5-9b8f-b81fc84159f7	adr_accept_hod_req	Accept change request from head of department and respond	Receive and act on a change request sent up from the head of department	adr_hod_change_req	t	220
ed99cc70-b5e8-4432-9ad0-94e7768569b2	adr_view_final_letter	View approval or rejection letter from top management	Downloadable final letter carrying all three e-signatures	adr_final_feedback	t	230
bdb69a9a-728f-4158-9ae1-57e62ac34e4b	adr_hub_app_review	Application review	Review staff applications via the ADR workspace	adr_hub_review	t	500
b8eaf02a-6d6d-44b6-b062-780adb3280fa	adr_hub_cr_send	Send Change Request	Send a change request to HoD or Staff applicant	adr_hub_change_request	t	510
4f616917-debe-4e55-826b-1c89fe986a69	adr_hub_cr_view	View Change Requests	View outstanding and resolved change requests	adr_hub_change_request	t	511
6711de54-654e-4eeb-b79c-99c8cac2cf22	adr_hub_fb_send	Send Review Feedback	Issue the signed ADR review feedback to Top Management	adr_hub_review_feedback	t	520
42eafd68-d2f0-4dcb-8f7b-110800cc8298	adr_hub_fb_reports	Final Application Reports	View and forward final reports from Top Management to HoD	adr_hub_review_feedback	t	521
064c28ae-a285-4eec-b76d-16c85cc421ea	top_assess_details	Assess application details	Read and assess the staff further studies application	top_review	f	300
5c09e94f-5bb0-4110-86e4-4115c4b40c14	top_review_doc	Review application document	Open and review attached application documents	top_review	t	301
3f6ddede-eff8-4423-817f-af71b5b099c5	top_review_adr_fb	Review assistant director review feedback	Read the review feedback submitted by the assistant director	top_review	t	302
40d2b680-f470-43c0-a43d-dd75534c252b	top_send_changes	Send change requests to assistant director	Request amendments from the assistant director	top_review	t	303
632659e7-42d5-4a41-a64e-1eb2dc10337f	top_create_feedback	Create review feedback	Use the review-feedback template and apply top management e-signature	top_send_feedback	t	310
a65e93e5-e57f-47b6-a10b-a19d9b7696eb	top_send_final	Send final review feedback to assistant director	Final letter with third e-signature - propagates down the review chain	top_send_feedback	t	311
1a78ef33-0bcd-4e23-9215-a455e37ead69	top_accept_adr_req	Accept change request from assistant director and respond	Receive and act on a change request sent up from the assistant director	top_adr_change_req	t	320
9095878d-7d5b-4ca1-a7c5-60c81890318a	top_mgmt_app_review	Top Mgmt - Application Review	Access the top management application review queue	top_mgmt_review	t	50
86280174-57de-4ee2-adab-5a9e2fc4df80	top_mgmt_cr_send	Top Mgmt - Send Change Request	Send a change request to the Assistant Director	top_mgmt_change_request	t	51
8ad19d35-7d1d-467a-a3fa-707c89fa0366	top_mgmt_cr_view	Top Mgmt - View Change Requests	View all sent change requests	top_mgmt_change_request	t	52
5fec7f6c-04d0-41de-ad81-18fce3e357f4	top_mgmt_fb_send	Top Mgmt - Send Review Feedback	Send final review feedback / formal report	top_mgmt_review_feedback	t	53
0a9773fa-b7ca-4bfd-b639-2f96c256e34a	top_mgmt_fb_reports	Top Mgmt - Final Application Reports	View archive of final application reports	top_mgmt_review_feedback	t	54
1d9dafa9-3ed9-4cca-8efd-e75693f8511c	hr_view_requests	View all student field requests	Open and view a field request; delete a request after assessment	hr_field_requests	t	50
52da58cd-1e77-498e-8f02-4e6e8dac43a5	hr_assess_request	Assess field request	View student details and downloadable application letter from the university	hr_field_requests	t	51
8bbb87e6-40d3-4314-9246-5772fd75cd7c	hr_feedback_student	Send feedback to student	Deliver feedback via in-system message or email notification	hr_field_requests	t	52
1cfa9748-8da6-4c9b-b25a-13870d001468	hr_dept_handoff	Send feedback of approved student to head of department	Forward approved student field request to the head of department	hr_dept_handoff	t	60
ba40e530-282b-4e9e-9cc5-e58561dc31d5	field.requestfeedback	field application report		field requests	f	0
fd1a7794-a171-4c47-a65b-9960a1d48b69	send_furtherrequest	send furtherrequest		Further studies	f	0
ea98c9b8-c803-4c3f-a66c-8ffb6dcc323c	payment:view	View Payments	View payment records and history	finance	f	20
868e922d-2d71-42bf-bac5-828823eeb94b	payment:approve	Approve Payments	Approve or reject payment requests	finance	f	21
\.


--
-- Data for Name: staff_capability_overrides; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staff_capability_overrides (id, mode, is_active, capability_id, staff_id) FROM stdin;
\.


--
-- Data for Name: staff_role_capabilities; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staff_role_capabilities (id, is_active, capability_id, role_id) FROM stdin;
36393080-d86c-4d51-9497-d8232a76ba7a	t	9f0e5203-5039-4398-b444-82439e72e174	68f3cc37-ad2c-4173-a15a-82442095431a
385f1cd7-92bb-405b-b9e8-140c93c3f1d3	t	49d5b3db-fc83-475b-8094-02e4487a551e	68f3cc37-ad2c-4173-a15a-82442095431a
4d97efb3-d610-4161-8f09-528737e04471	t	43071674-f035-49c3-8c5b-26af09735ac4	68f3cc37-ad2c-4173-a15a-82442095431a
0cdb5f81-c5ad-46e7-b092-ab5ffba2324a	t	893ef79e-cb6e-4542-9b5f-59d8eb56dc3a	68f3cc37-ad2c-4173-a15a-82442095431a
8b6df60f-a63e-4f91-8715-9afb0a52ed9f	t	508afb8f-4081-42cb-80f6-276e76a145a1	68f3cc37-ad2c-4173-a15a-82442095431a
714285fe-b564-454f-b8ac-b7ef9054f7ce	t	97d22843-a3a0-4d5e-804a-7529de6b51fc	68f3cc37-ad2c-4173-a15a-82442095431a
35dfc407-2645-46cd-9d8a-20c00135f2e8	t	24af9228-9469-462c-bae6-a4fbd9e679ca	68f3cc37-ad2c-4173-a15a-82442095431a
7d8f7786-a2ab-43f7-82a1-d4dc96f6acd7	t	533cc3b2-f242-41a9-8b2a-bd046663e736	68f3cc37-ad2c-4173-a15a-82442095431a
312e353f-d639-4214-9c80-a3cf0495b570	t	cba3c5c0-f53e-4752-90e5-22fb10a22f72	68f3cc37-ad2c-4173-a15a-82442095431a
dd29b02c-0ea8-4b87-b298-bba7db4418c3	t	871d71fc-4abd-4122-b70d-20410e250786	68f3cc37-ad2c-4173-a15a-82442095431a
eed573f1-4e19-4a74-a713-2388c8cdb856	t	9f0e5203-5039-4398-b444-82439e72e174	d68edf98-e629-46de-b192-76aa092338c3
94404b72-1b95-4c21-876a-40c0d17a0b94	t	8bbb87e6-40d3-4314-9246-5772fd75cd7c	d68edf98-e629-46de-b192-76aa092338c3
2a71618b-0a65-44a8-bc25-5f07e2b512f4	t	49d5b3db-fc83-475b-8094-02e4487a551e	d68edf98-e629-46de-b192-76aa092338c3
024bd51a-b44e-4914-866a-e00ea4109c37	t	1cfa9748-8da6-4c9b-b25a-13870d001468	d68edf98-e629-46de-b192-76aa092338c3
334c9350-5de3-41b1-8616-47558adcdf0d	t	52da58cd-1e77-498e-8f02-4e6e8dac43a5	d68edf98-e629-46de-b192-76aa092338c3
eb6985a3-5f32-4ac7-bd1f-522303353cf4	t	1d9dafa9-3ed9-4cca-8efd-e75693f8511c	d68edf98-e629-46de-b192-76aa092338c3
5a9cf724-b729-47ff-8273-93201fb2dd6c	t	43071674-f035-49c3-8c5b-26af09735ac4	d68edf98-e629-46de-b192-76aa092338c3
92a7a93d-c7ea-4138-99ae-744e555642be	t	893ef79e-cb6e-4542-9b5f-59d8eb56dc3a	d68edf98-e629-46de-b192-76aa092338c3
dc103c2f-8a35-420d-9643-bdb938112800	t	508afb8f-4081-42cb-80f6-276e76a145a1	d68edf98-e629-46de-b192-76aa092338c3
c22dc8db-d68a-4997-8fa8-c20ec5fa86bb	t	97d22843-a3a0-4d5e-804a-7529de6b51fc	d68edf98-e629-46de-b192-76aa092338c3
edc26ef2-c73b-4f1f-875a-b9704d099882	t	24af9228-9469-462c-bae6-a4fbd9e679ca	d68edf98-e629-46de-b192-76aa092338c3
6e71b2c4-5245-4b2a-913d-972f2397c7e6	t	533cc3b2-f242-41a9-8b2a-bd046663e736	d68edf98-e629-46de-b192-76aa092338c3
3f5707f8-583d-419f-a4d0-510fa7a9b1ad	t	cba3c5c0-f53e-4752-90e5-22fb10a22f72	d68edf98-e629-46de-b192-76aa092338c3
cb6b5036-eeb3-4516-a703-9fbefd4a7108	t	871d71fc-4abd-4122-b70d-20410e250786	d68edf98-e629-46de-b192-76aa092338c3
3acaf7b1-0981-4657-968f-428b75544452	t	960c9535-e84b-44f8-8564-a4868c27cadd	d63dadf4-21a4-443d-b243-594d4dd58cd0
8fcce000-3bbe-441b-9b51-6c4f53af18e5	t	edf47faf-4c30-4463-aedd-76530101e6b1	d63dadf4-21a4-443d-b243-594d4dd58cd0
fffb5b95-4cd3-4659-a262-099497a58db7	t	3a4a75ec-6b9c-4d56-b428-43b0e0091906	d63dadf4-21a4-443d-b243-594d4dd58cd0
bd582845-314c-4b11-ba90-cb0b749be42b	t	49d5b3db-fc83-475b-8094-02e4487a551e	d63dadf4-21a4-443d-b243-594d4dd58cd0
94e9b3d3-d176-490e-b7a7-3db34feca589	t	508afb8f-4081-42cb-80f6-276e76a145a1	d63dadf4-21a4-443d-b243-594d4dd58cd0
2d282462-711e-4892-9c56-b65e7cdaf121	t	97d22843-a3a0-4d5e-804a-7529de6b51fc	d63dadf4-21a4-443d-b243-594d4dd58cd0
6f27cd58-7718-41cf-bcfc-c4a09f9a019f	t	ba427a9d-1b91-4b50-80f7-432b8625dfe3	d63dadf4-21a4-443d-b243-594d4dd58cd0
33cb0bba-a7b9-4055-8b0b-4c8e5536189f	t	533cc3b2-f242-41a9-8b2a-bd046663e736	d63dadf4-21a4-443d-b243-594d4dd58cd0
40b2f564-f649-41c2-b627-95767ee220ac	t	5ed6f5e9-6dfd-47cb-a225-a5dfa4987628	d63dadf4-21a4-443d-b243-594d4dd58cd0
dd679da2-8a96-42fe-b9bb-d5b5313c368f	t	bf9c1f07-b8cb-46f8-bce5-81020ee5e667	d63dadf4-21a4-443d-b243-594d4dd58cd0
a353b648-88b2-4fff-aadf-9325421eeaa9	t	3256842d-a34d-4a5d-9ada-ceefca922665	d63dadf4-21a4-443d-b243-594d4dd58cd0
92ea20df-c2a9-44e0-8bb5-70fd11119054	t	6ef928d7-0fc0-40f8-9e9f-8f7e0320523f	d63dadf4-21a4-443d-b243-594d4dd58cd0
8b89acca-60e5-4356-b952-5bd0248f0cac	t	9f0e5203-5039-4398-b444-82439e72e174	d63dadf4-21a4-443d-b243-594d4dd58cd0
60023574-b80d-49de-afc7-6b1d44b7b342	t	bf505455-f7a7-4ec5-9050-e5008f269806	d63dadf4-21a4-443d-b243-594d4dd58cd0
d8375389-4079-4f08-929e-152de9b77817	t	ec2237a3-6f2f-4d74-8791-a85d7b93a485	d63dadf4-21a4-443d-b243-594d4dd58cd0
b672aef9-5aa9-47b3-8c38-2e3030959518	t	49b5ff51-86b0-4c7c-89a1-275fb943d473	d63dadf4-21a4-443d-b243-594d4dd58cd0
2725b716-dcbb-4050-8dc5-d499705bf274	t	d02107f2-8cf5-40c7-88c6-ae65f0ee90fc	d63dadf4-21a4-443d-b243-594d4dd58cd0
d7022104-104f-46d6-ac20-4697e542ade4	t	7c402bc6-2765-4a6e-8a38-bfd39316695b	d63dadf4-21a4-443d-b243-594d4dd58cd0
75bae549-c667-4cc2-a4af-686ed5617a12	t	cba3c5c0-f53e-4752-90e5-22fb10a22f72	d63dadf4-21a4-443d-b243-594d4dd58cd0
2d228f9a-2c9d-4468-af9b-b84754fc4030	t	43071674-f035-49c3-8c5b-26af09735ac4	d63dadf4-21a4-443d-b243-594d4dd58cd0
677cc93e-a91d-4fd0-b851-9496a1d55667	t	893ef79e-cb6e-4542-9b5f-59d8eb56dc3a	d63dadf4-21a4-443d-b243-594d4dd58cd0
0ec957e6-f1ff-4a37-8352-9a4b8a2a6e24	t	2d70dc6c-6d45-4048-be03-eea032902624	d63dadf4-21a4-443d-b243-594d4dd58cd0
36748bd3-52c5-4e14-aaca-76a9bbdf64e9	t	24af9228-9469-462c-bae6-a4fbd9e679ca	d63dadf4-21a4-443d-b243-594d4dd58cd0
3aae439d-18a5-4366-a5ab-db592ddec2c7	t	871d71fc-4abd-4122-b70d-20410e250786	d63dadf4-21a4-443d-b243-594d4dd58cd0
855942da-7e6e-4b9d-b484-709b4873e20e	t	ed99cc70-b5e8-4432-9ad0-94e7768569b2	827aeb91-a4ee-4ba0-b750-9a66c45e012e
908cf01d-7d70-4c62-9d20-9fed438358d5	t	aa9880a7-92fe-41ab-b0d6-38d49fcaa33a	827aeb91-a4ee-4ba0-b750-9a66c45e012e
1790f011-ec42-4e18-b6b7-273ae1464189	t	7b0c20a9-48ea-4ad5-9b8f-b81fc84159f7	827aeb91-a4ee-4ba0-b750-9a66c45e012e
33c94492-2848-4aaa-9bfb-36e6982e979f	t	42eafd68-d2f0-4dcb-8f7b-110800cc8298	827aeb91-a4ee-4ba0-b750-9a66c45e012e
164e86c3-1a6e-42c8-b596-bf6fb8404272	t	93a6d4ab-e42c-4a14-8baa-f4475872f0bf	827aeb91-a4ee-4ba0-b750-9a66c45e012e
7c4acf04-c43c-4a85-b9b6-4bfc6bb162d1	t	49d5b3db-fc83-475b-8094-02e4487a551e	827aeb91-a4ee-4ba0-b750-9a66c45e012e
bc377da9-75ba-4e5c-b912-a0efb8f7fbc7	t	c77f55ca-1b93-45bc-ad8e-97c80d3036f5	827aeb91-a4ee-4ba0-b750-9a66c45e012e
40e1f875-5481-4aee-ad93-e1692d055ae7	t	508afb8f-4081-42cb-80f6-276e76a145a1	827aeb91-a4ee-4ba0-b750-9a66c45e012e
4ff6196a-2876-4691-94b4-bfeb485fa309	t	97d22843-a3a0-4d5e-804a-7529de6b51fc	827aeb91-a4ee-4ba0-b750-9a66c45e012e
967d870e-7f92-4564-854f-98d8ced37099	t	533cc3b2-f242-41a9-8b2a-bd046663e736	827aeb91-a4ee-4ba0-b750-9a66c45e012e
a5a32f0e-de06-4761-a5e7-5a7f31d262ee	t	6711de54-654e-4eeb-b79c-99c8cac2cf22	827aeb91-a4ee-4ba0-b750-9a66c45e012e
d4fbe687-52ed-4e7f-8aa2-27d54f286679	t	9a6e5819-dc2d-42c4-bdd6-98d839b3b88e	827aeb91-a4ee-4ba0-b750-9a66c45e012e
bdef283c-3302-4bcc-b337-72420dae3812	t	b8eaf02a-6d6d-44b6-b062-780adb3280fa	827aeb91-a4ee-4ba0-b750-9a66c45e012e
ce8dc284-8e44-4b3b-9997-97c7692182b2	t	2e847566-f52e-46b8-8d90-e2c54037918f	827aeb91-a4ee-4ba0-b750-9a66c45e012e
aaba0b96-76ce-4007-bd4a-3d48f005d4e2	t	9f0e5203-5039-4398-b444-82439e72e174	827aeb91-a4ee-4ba0-b750-9a66c45e012e
6120f2b7-45f5-454c-8bb7-a58792c26209	t	4f616917-debe-4e55-826b-1c89fe986a69	827aeb91-a4ee-4ba0-b750-9a66c45e012e
873703fc-5330-40d9-91be-2c62e59c9e2c	t	cba3c5c0-f53e-4752-90e5-22fb10a22f72	827aeb91-a4ee-4ba0-b750-9a66c45e012e
471aead1-1657-4cca-b032-e4f9f22285cd	t	43071674-f035-49c3-8c5b-26af09735ac4	827aeb91-a4ee-4ba0-b750-9a66c45e012e
9ef2253c-cd60-4195-97bd-30aa2337f069	t	893ef79e-cb6e-4542-9b5f-59d8eb56dc3a	827aeb91-a4ee-4ba0-b750-9a66c45e012e
6c2974a6-b671-48ad-a65f-f79cac8cb08e	t	1e82ef2c-29ed-4097-8b76-b64ac160f433	827aeb91-a4ee-4ba0-b750-9a66c45e012e
d654aa2d-bbf2-4916-914e-1408ad0bbcdf	t	24af9228-9469-462c-bae6-a4fbd9e679ca	827aeb91-a4ee-4ba0-b750-9a66c45e012e
045d271e-80fa-40c5-a4ae-79e1107f9f1e	t	871d71fc-4abd-4122-b70d-20410e250786	827aeb91-a4ee-4ba0-b750-9a66c45e012e
47b75b38-cc27-4dcd-9320-1441c9bd6399	t	bdb69a9a-728f-4158-9ae1-57e62ac34e4b	827aeb91-a4ee-4ba0-b750-9a66c45e012e
6f9a066b-eb37-4852-9a2d-2cebc212e93d	t	40d2b680-f470-43c0-a43d-dd75534c252b	29c2f168-0243-416d-b24a-2f341dce05f5
b60a59e1-efd7-4c3d-9009-d58dd25a6679	t	5fec7f6c-04d0-41de-ad81-18fce3e357f4	29c2f168-0243-416d-b24a-2f341dce05f5
6b47ffb8-3a10-4643-b902-76a15a327f91	t	a65e93e5-e57f-47b6-a10b-a19d9b7696eb	29c2f168-0243-416d-b24a-2f341dce05f5
98281b68-ff67-4d07-bb67-8dbabeda8d3b	t	49d5b3db-fc83-475b-8094-02e4487a551e	29c2f168-0243-416d-b24a-2f341dce05f5
3cccc12d-b67d-4603-b95c-771e6a975eb3	t	1a78ef33-0bcd-4e23-9215-a455e37ead69	29c2f168-0243-416d-b24a-2f341dce05f5
a83e4054-556c-450b-a7a2-14ee3b9804e3	t	508afb8f-4081-42cb-80f6-276e76a145a1	29c2f168-0243-416d-b24a-2f341dce05f5
2ac7b720-38fd-4d7e-bd55-e1d5199b4b63	t	97d22843-a3a0-4d5e-804a-7529de6b51fc	29c2f168-0243-416d-b24a-2f341dce05f5
27f0f469-7899-4cea-9d19-4bd9fe5c7b4f	t	533cc3b2-f242-41a9-8b2a-bd046663e736	29c2f168-0243-416d-b24a-2f341dce05f5
45bbc74d-1417-407a-bc44-659b0e5753ba	t	8ad19d35-7d1d-467a-a3fa-707c89fa0366	29c2f168-0243-416d-b24a-2f341dce05f5
58054de5-8fcc-4c8d-991d-433c73895422	t	9f0e5203-5039-4398-b444-82439e72e174	29c2f168-0243-416d-b24a-2f341dce05f5
c88f6d1b-6652-4830-b7e1-7ca7cf90bd3a	t	632659e7-42d5-4a41-a64e-1eb2dc10337f	29c2f168-0243-416d-b24a-2f341dce05f5
e24c0e2b-3de4-42e3-a50a-3f66fa142dbb	t	5c09e94f-5bb0-4110-86e4-4115c4b40c14	29c2f168-0243-416d-b24a-2f341dce05f5
e03b114a-5284-4786-899c-cabb691c86c0	t	cba3c5c0-f53e-4752-90e5-22fb10a22f72	29c2f168-0243-416d-b24a-2f341dce05f5
4326be07-5e9d-4147-87a4-304c85a5e606	t	3f6ddede-eff8-4423-817f-af71b5b099c5	29c2f168-0243-416d-b24a-2f341dce05f5
437a7d00-4af8-407a-aa04-6475386ef3f8	t	43071674-f035-49c3-8c5b-26af09735ac4	29c2f168-0243-416d-b24a-2f341dce05f5
26769b05-ba39-45c6-bd83-0c493b6f20e4	t	893ef79e-cb6e-4542-9b5f-59d8eb56dc3a	29c2f168-0243-416d-b24a-2f341dce05f5
d67aae8a-ef09-42da-9c36-1926198b8cf5	t	86280174-57de-4ee2-adab-5a9e2fc4df80	29c2f168-0243-416d-b24a-2f341dce05f5
f1aa8213-0426-4cac-8790-7c846a4d7678	t	24af9228-9469-462c-bae6-a4fbd9e679ca	29c2f168-0243-416d-b24a-2f341dce05f5
c020a685-c146-4321-b9c0-804511c47f3f	t	0a9773fa-b7ca-4bfd-b639-2f96c256e34a	29c2f168-0243-416d-b24a-2f341dce05f5
d230152b-0c67-43f3-887d-b69d32c64a0d	t	9095878d-7d5b-4ca1-a7c5-60c81890318a	29c2f168-0243-416d-b24a-2f341dce05f5
1231d184-cf47-431d-9d4c-b8d7fbcbd4ca	t	871d71fc-4abd-4122-b70d-20410e250786	29c2f168-0243-416d-b24a-2f341dce05f5
\.


--
-- Data for Name: staff_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.staff_roles (id, code, name, description, is_active, sort_order) FROM stdin;
68f3cc37-ad2c-4173-a15a-82442095431a	staff	Staff	Base role for all hospital staff — further studies application, tracking, feedback, and notifications	t	1
d68edf98-e629-46de-b192-76aa092338c3	hr_manager	Human resource manager	Inherits Staff; adds student field request management and department handoff	t	2
d63dadf4-21a4-443d-b243-594d4dd58cd0	hod	Head of department	Inherits Staff; reviews staff applications, creates signed feedback, views HR-approved students	t	3
827aeb91-a4ee-4ba0-b750-9a66c45e012e	asst_director	Assistant director	Inherits Staff; reviews staff applications and HoD feedback, creates signed feedback to top management	t	4
29c2f168-0243-416d-b24a-2f341dce05f5	top_management	Top management	Inherits Staff; gives final decision, issues the three-signature approval letter	t	5
\.


--
-- Data for Name: student_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.student_profiles (id, registration_no, full_name, programme, faculty, year_of_study, phone, dob, university, supervisor_id, user_id, contact_email, dashboard_notes, gender, hospital_department_id, level_of_study, department_entity_id, faculty_entity_id) FROM stdin;
\.


--
-- Data for Name: university_departments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.university_departments (id, name, sort_order, faculty_id, is_active) FROM stdin;
02e9994a-ad9f-4620-87fd-49024e5786ee	BBIT	0	8cd8ceb3-8078-4ab2-834f-cc6441512585	t
0132af9e-4d14-4a3d-8b20-525b888113b8	Nursing	0	7cd2d7de-d5ee-4de8-8f21-4141c8240ac8	t
a8ccfddc-75f9-43fe-9577-b36535a152df	Bachelor Biology and chemistry	1	7cd2d7de-d5ee-4de8-8f21-4141c8240ac8	t
\.


--
-- Data for Name: university_faculties; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.university_faculties (id, name, sort_order, is_active) FROM stdin;
8cd8ceb3-8078-4ab2-834f-cc6441512585	Busness Administration	0	t
7cd2d7de-d5ee-4de8-8f21-4141c8240ac8	Health	1	t
3485af3a-248d-47c8-a3f8-60d5fa25fd82	Education	2	t
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (password, last_login, is_superuser, first_name, last_name, email, is_staff, is_active, date_joined, id, username, role, module, is_first_login, created_at) FROM stdin;
pbkdf2_sha256$1200000$K6rKNqEJXUtEvZx7t9QeFw$59HndI/3ksYFd9pws1NMXErKsecHacqHBuG1E3ba2jM=	\N	t			nabiyumusta@gmail.com	t	t	2026-06-20 22:21:48.529332+03	d5bbec08-f5dd-4f51-8f6e-4bda619b6c5e	postgre	sysadmin	admin	f	2026-06-20 22:21:49.277103+03
pbkdf2_sha256$1200000$QiTQ87EUfLuX6od7fV88xa$TDt9OEUrBC70ihtXj7UIJn+qn/VkbB7BBKcQjY5NUho=	\N	f	HospitalAdmin		dogo25midi@gmail.com	t	t	2026-06-20 22:27:26.065366+03	44bb494c-821c-4052-8aab-a30d8c67cb25	Hospital123	hospital_admin	admin	t	2026-06-20 22:27:26.830417+03
pbkdf2_sha256$1200000$a0mnas5VepnbJMz0Fn0wyp$/Aedc47KresWKxsxjoCDYGznPodMp8fI2QnFgXi2Vzw=	\N	f	SaidatAdmin		faat05hi@gmail.com	t	t	2026-06-21 10:38:28.698546+03	e0564f91-60d7-4969-8337-a9d869e59fbf	Saidat	hospital_admin	admin	t	2026-06-21 10:38:29.442676+03
pbkdf2_sha256$1200000$bA6Q55cmNl4cCgniJjuEbs$a8jmfTyfsneuRQHsk+64ezK3HOAofjBeFNcpIWFq4Rw=	\N	f	SalumAdmin		ksalum734@gmail.com	t	t	2026-06-22 11:19:17.569423+03	8686a2da-0040-4732-8431-ebf64d56e6d4	Salum	hospital_admin	admin	f	2026-06-22 11:19:18.366953+03
\.


--
-- Data for Name: users_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: users_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 112, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 28, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 62, true);


--
-- Name: users_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_groups_id_seq', 1, false);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_permissions_id_seq', 1, false);


--
-- Name: application_change_requests application_change_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_change_requests
    ADD CONSTRAINT application_change_requests_pkey PRIMARY KEY (id);


--
-- Name: application_documents application_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_documents
    ADD CONSTRAINT application_documents_pkey PRIMARY KEY (id);


--
-- Name: applications applications_app_ref_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_app_ref_key UNIQUE (app_ref);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: department_hod_assignments department_hod_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department_hod_assignments
    ADD CONSTRAINT department_hod_assignments_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: hospital_staff employee_profiles_employee_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_employee_number_key UNIQUE (staff_number);


--
-- Name: hospital_staff employee_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_pkey PRIMARY KEY (id);


--
-- Name: hospital_staff employee_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_user_id_key UNIQUE (user_id);


--
-- Name: hospital_application_document_kinds hospital_application_document_kinds_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_application_document_kinds
    ADD CONSTRAINT hospital_application_document_kinds_code_key UNIQUE (code);


--
-- Name: hospital_application_document_kinds hospital_application_document_kinds_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_application_document_kinds
    ADD CONSTRAINT hospital_application_document_kinds_pkey PRIMARY KEY (id);


--
-- Name: hospital_departments hospital_departments_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_departments
    ADD CONSTRAINT hospital_departments_name_key UNIQUE (name);


--
-- Name: hospital_departments hospital_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_departments
    ADD CONSTRAINT hospital_departments_pkey PRIMARY KEY (id);


--
-- Name: hospital_designations hospital_designations_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_designations
    ADD CONSTRAINT hospital_designations_name_key UNIQUE (name);


--
-- Name: hospital_designations hospital_designations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_designations
    ADD CONSTRAINT hospital_designations_pkey PRIMARY KEY (id);


--
-- Name: hospital_sponsorship_types hospital_sponsorship_types_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_sponsorship_types
    ADD CONSTRAINT hospital_sponsorship_types_name_key UNIQUE (name);


--
-- Name: hospital_sponsorship_types hospital_sponsorship_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_sponsorship_types
    ADD CONSTRAINT hospital_sponsorship_types_pkey PRIMARY KEY (id);


--
-- Name: hospital_working_sites hospital_working_sites_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_working_sites
    ADD CONSTRAINT hospital_working_sites_name_key UNIQUE (name);


--
-- Name: hospital_working_sites hospital_working_sites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_working_sites
    ADD CONSTRAINT hospital_working_sites_pkey PRIMARY KEY (id);


--
-- Name: import_batches import_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.import_batches
    ADD CONSTRAINT import_batches_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: review_trail review_trail_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_trail
    ADD CONSTRAINT review_trail_pkey PRIMARY KEY (id);


--
-- Name: staff_capabilities_catalog staff_capabilities_catalog_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_capabilities_catalog
    ADD CONSTRAINT staff_capabilities_catalog_code_key UNIQUE (code);


--
-- Name: staff_capabilities_catalog staff_capabilities_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_capabilities_catalog
    ADD CONSTRAINT staff_capabilities_catalog_pkey PRIMARY KEY (id);


--
-- Name: staff_capability_overrides staff_capability_overrides_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_capability_overrides
    ADD CONSTRAINT staff_capability_overrides_pkey PRIMARY KEY (id);


--
-- Name: staff_role_capabilities staff_role_capabilities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_role_capabilities
    ADD CONSTRAINT staff_role_capabilities_pkey PRIMARY KEY (id);


--
-- Name: staff_roles staff_roles_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_roles
    ADD CONSTRAINT staff_roles_code_key UNIQUE (code);


--
-- Name: staff_roles staff_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_roles
    ADD CONSTRAINT staff_roles_pkey PRIMARY KEY (id);


--
-- Name: student_profiles student_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_pkey PRIMARY KEY (id);


--
-- Name: student_profiles student_profiles_registration_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_registration_no_key UNIQUE (registration_no);


--
-- Name: student_profiles student_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_user_id_key UNIQUE (user_id);


--
-- Name: department_hod_assignments uniq_department_hod_assignment; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department_hod_assignments
    ADD CONSTRAINT uniq_department_hod_assignment UNIQUE (department_id);


--
-- Name: staff_capability_overrides uniq_staff_capability_override; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_capability_overrides
    ADD CONSTRAINT uniq_staff_capability_override UNIQUE (staff_id, capability_id, mode);


--
-- Name: staff_role_capabilities uniq_staff_role_capability; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_role_capabilities
    ADD CONSTRAINT uniq_staff_role_capability UNIQUE (role_id, capability_id);


--
-- Name: university_departments uniq_university_department_per_faculty; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.university_departments
    ADD CONSTRAINT uniq_university_department_per_faculty UNIQUE (faculty_id, name);


--
-- Name: university_departments university_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.university_departments
    ADD CONSTRAINT university_departments_pkey PRIMARY KEY (id);


--
-- Name: university_faculties university_faculties_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.university_faculties
    ADD CONSTRAINT university_faculties_name_key UNIQUE (name);


--
-- Name: university_faculties university_faculties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.university_faculties
    ADD CONSTRAINT university_faculties_pkey PRIMARY KEY (id);


--
-- Name: users_groups users_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_pkey PRIMARY KEY (id);


--
-- Name: users_groups users_groups_user_id_group_id_fc7788e8_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_group_id_fc7788e8_uniq UNIQUE (user_id, group_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_user_id_permission_id_3b86cbdf_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_permission_id_3b86cbdf_uniq UNIQUE (user_id, permission_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: application_applica_e9ee09_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX application_applica_e9ee09_idx ON public.applications USING btree (applicant_id, status);


--
-- Name: application_change_requests_application_id_3c947242; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX application_change_requests_application_id_3c947242 ON public.application_change_requests USING btree (application_id);


--
-- Name: application_change_requests_sender_id_914f3b80; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX application_change_requests_sender_id_914f3b80 ON public.application_change_requests USING btree (sender_id);


--
-- Name: application_documents_application_id_fe7e9522; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX application_documents_application_id_fe7e9522 ON public.application_documents USING btree (application_id);


--
-- Name: application_status_f8f5ce_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX application_status_f8f5ce_idx ON public.applications USING btree (status, current_stage);


--
-- Name: applications_app_ref_52ca47a8_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX applications_app_ref_52ca47a8_like ON public.applications USING btree (app_ref varchar_pattern_ops);


--
-- Name: applications_applicant_id_0f5ee165; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX applications_applicant_id_0f5ee165 ON public.applications USING btree (applicant_id);


--
-- Name: applications_hospital_department_id_af1d18c6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX applications_hospital_department_id_af1d18c6 ON public.applications USING btree (hospital_department_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: department_hod_assignments_department_id_9ea9ed14; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX department_hod_assignments_department_id_9ea9ed14 ON public.department_hod_assignments USING btree (department_id);


--
-- Name: department_hod_assignments_hod_user_id_b42e6f4c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX department_hod_assignments_hod_user_id_b42e6f4c ON public.department_hod_assignments USING btree (hod_user_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: employee_profiles_department_id_cfac7436; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employee_profiles_department_id_cfac7436 ON public.hospital_staff USING btree (department_id);


--
-- Name: employee_profiles_designation_id_c471d8a8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employee_profiles_designation_id_c471d8a8 ON public.hospital_staff USING btree (designation_id);


--
-- Name: employee_profiles_employee_number_6b982a33_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employee_profiles_employee_number_6b982a33_like ON public.hospital_staff USING btree (staff_number varchar_pattern_ops);


--
-- Name: employee_profiles_hod_id_fa9a3d13; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employee_profiles_hod_id_fa9a3d13 ON public.hospital_staff USING btree (hod_id);


--
-- Name: employee_profiles_working_site_id_8008b9b7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX employee_profiles_working_site_id_8008b9b7 ON public.hospital_staff USING btree (working_site_id);


--
-- Name: hospital_application_document_kinds_code_877f0888_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hospital_application_document_kinds_code_877f0888_like ON public.hospital_application_document_kinds USING btree (code varchar_pattern_ops);


--
-- Name: hospital_departments_name_61beb336_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hospital_departments_name_61beb336_like ON public.hospital_departments USING btree (name varchar_pattern_ops);


--
-- Name: hospital_designations_name_dd566948_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hospital_designations_name_dd566948_like ON public.hospital_designations USING btree (name varchar_pattern_ops);


--
-- Name: hospital_sponsorship_types_name_81028ee0_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hospital_sponsorship_types_name_81028ee0_like ON public.hospital_sponsorship_types USING btree (name varchar_pattern_ops);


--
-- Name: hospital_staff_staff_role_id_e881277e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hospital_staff_staff_role_id_e881277e ON public.hospital_staff USING btree (staff_role_id);


--
-- Name: hospital_working_sites_name_3fa72660_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX hospital_working_sites_name_3fa72660_like ON public.hospital_working_sites USING btree (name varchar_pattern_ops);


--
-- Name: import_batches_imported_by_id_52313233; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX import_batches_imported_by_id_52313233 ON public.import_batches USING btree (imported_by_id);


--
-- Name: notif_parent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notif_parent_idx ON public.notifications USING btree (parent_id);


--
-- Name: notificatio_recipie_583549_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notificatio_recipie_583549_idx ON public.notifications USING btree (recipient_id, is_read);


--
-- Name: notifications_parent_id_2d419239; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_parent_id_2d419239 ON public.notifications USING btree (parent_id);


--
-- Name: notifications_recipient_id_e1133bac; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_recipient_id_e1133bac ON public.notifications USING btree (recipient_id);


--
-- Name: notifications_sender_id_57e62d28; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_sender_id_57e62d28 ON public.notifications USING btree (sender_id);


--
-- Name: review_trail_application_id_7038db39; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_trail_application_id_7038db39 ON public.review_trail USING btree (application_id);


--
-- Name: review_trail_reviewer_id_558887fe; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_trail_reviewer_id_558887fe ON public.review_trail USING btree (reviewer_id);


--
-- Name: staff_capabilities_catalog_code_30e6dd85_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX staff_capabilities_catalog_code_30e6dd85_like ON public.staff_capabilities_catalog USING btree (code varchar_pattern_ops);


--
-- Name: staff_capability_overrides_capability_id_8b2b9b19; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX staff_capability_overrides_capability_id_8b2b9b19 ON public.staff_capability_overrides USING btree (capability_id);


--
-- Name: staff_capability_overrides_staff_id_d1b4b15e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX staff_capability_overrides_staff_id_d1b4b15e ON public.staff_capability_overrides USING btree (staff_id);


--
-- Name: staff_role_capabilities_capability_id_a264d008; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX staff_role_capabilities_capability_id_a264d008 ON public.staff_role_capabilities USING btree (capability_id);


--
-- Name: staff_role_capabilities_role_id_bb650cb4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX staff_role_capabilities_role_id_bb650cb4 ON public.staff_role_capabilities USING btree (role_id);


--
-- Name: staff_roles_code_840f7694_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX staff_roles_code_840f7694_like ON public.staff_roles USING btree (code varchar_pattern_ops);


--
-- Name: student_profiles_department_entity_id_8caabb50; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX student_profiles_department_entity_id_8caabb50 ON public.student_profiles USING btree (department_entity_id);


--
-- Name: student_profiles_faculty_entity_id_6e4aca31; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX student_profiles_faculty_entity_id_6e4aca31 ON public.student_profiles USING btree (faculty_entity_id);


--
-- Name: student_profiles_hospital_department_id_f9dbbb22; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX student_profiles_hospital_department_id_f9dbbb22 ON public.student_profiles USING btree (hospital_department_id);


--
-- Name: student_profiles_registration_no_57b0f01d_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX student_profiles_registration_no_57b0f01d_like ON public.student_profiles USING btree (registration_no varchar_pattern_ops);


--
-- Name: student_profiles_supervisor_id_791679ac; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX student_profiles_supervisor_id_791679ac ON public.student_profiles USING btree (supervisor_id);


--
-- Name: university_departments_faculty_id_8b44f025; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX university_departments_faculty_id_8b44f025 ON public.university_departments USING btree (faculty_id);


--
-- Name: university_faculties_name_c116fa31_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX university_faculties_name_c116fa31_like ON public.university_faculties USING btree (name varchar_pattern_ops);


--
-- Name: users_groups_group_id_2f3517aa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_group_id_2f3517aa ON public.users_groups USING btree (group_id);


--
-- Name: users_groups_user_id_f500bee5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_user_id_f500bee5 ON public.users_groups USING btree (user_id);


--
-- Name: users_user_permissions_permission_id_6d08dcd2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_permission_id_6d08dcd2 ON public.users_user_permissions USING btree (permission_id);


--
-- Name: users_user_permissions_user_id_92473840; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_user_id_92473840 ON public.users_user_permissions USING btree (user_id);


--
-- Name: users_username_e8658fc8_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_username_e8658fc8_like ON public.users USING btree (username varchar_pattern_ops);


--
-- Name: application_change_requests application_change_r_application_id_3c947242_fk_applicati; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_change_requests
    ADD CONSTRAINT application_change_r_application_id_3c947242_fk_applicati FOREIGN KEY (application_id) REFERENCES public.applications(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: application_change_requests application_change_requests_sender_id_914f3b80_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_change_requests
    ADD CONSTRAINT application_change_requests_sender_id_914f3b80_fk_users_id FOREIGN KEY (sender_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: application_documents application_document_application_id_fe7e9522_fk_applicati; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_documents
    ADD CONSTRAINT application_document_application_id_fe7e9522_fk_applicati FOREIGN KEY (application_id) REFERENCES public.applications(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: applications applications_applicant_id_0f5ee165_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_applicant_id_0f5ee165_fk_users_id FOREIGN KEY (applicant_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: applications applications_hospital_department__af1d18c6_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_hospital_department__af1d18c6_fk_hospital_ FOREIGN KEY (hospital_department_id) REFERENCES public.hospital_departments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: department_hod_assignments department_hod_assig_department_id_9ea9ed14_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department_hod_assignments
    ADD CONSTRAINT department_hod_assig_department_id_9ea9ed14_fk_hospital_ FOREIGN KEY (department_id) REFERENCES public.hospital_departments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: department_hod_assignments department_hod_assignments_hod_user_id_b42e6f4c_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.department_hod_assignments
    ADD CONSTRAINT department_hod_assignments_hod_user_id_b42e6f4c_fk_users_id FOREIGN KEY (hod_user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hospital_staff employee_profiles_department_id_cfac7436_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_department_id_cfac7436_fk_hospital_ FOREIGN KEY (department_id) REFERENCES public.hospital_departments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hospital_staff employee_profiles_designation_id_c471d8a8_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_designation_id_c471d8a8_fk_hospital_ FOREIGN KEY (designation_id) REFERENCES public.hospital_designations(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hospital_staff employee_profiles_hod_id_fa9a3d13_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_hod_id_fa9a3d13_fk_users_id FOREIGN KEY (hod_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hospital_staff employee_profiles_user_id_a490e3b4_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_user_id_a490e3b4_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hospital_staff employee_profiles_working_site_id_8008b9b7_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT employee_profiles_working_site_id_8008b9b7_fk_hospital_ FOREIGN KEY (working_site_id) REFERENCES public.hospital_working_sites(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: hospital_staff hospital_staff_staff_role_id_e881277e_fk_staff_roles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hospital_staff
    ADD CONSTRAINT hospital_staff_staff_role_id_e881277e_fk_staff_roles_id FOREIGN KEY (staff_role_id) REFERENCES public.staff_roles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: import_batches import_batches_imported_by_id_52313233_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.import_batches
    ADD CONSTRAINT import_batches_imported_by_id_52313233_fk_users_id FOREIGN KEY (imported_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications notifications_parent_id_2d419239_fk_notifications_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_parent_id_2d419239_fk_notifications_id FOREIGN KEY (parent_id) REFERENCES public.notifications(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications notifications_recipient_id_e1133bac_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_recipient_id_e1133bac_fk_users_id FOREIGN KEY (recipient_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications notifications_sender_id_57e62d28_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_sender_id_57e62d28_fk_users_id FOREIGN KEY (sender_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_trail review_trail_application_id_7038db39_fk_applications_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_trail
    ADD CONSTRAINT review_trail_application_id_7038db39_fk_applications_id FOREIGN KEY (application_id) REFERENCES public.applications(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_trail review_trail_reviewer_id_558887fe_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_trail
    ADD CONSTRAINT review_trail_reviewer_id_558887fe_fk_users_id FOREIGN KEY (reviewer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: staff_capability_overrides staff_capability_ove_capability_id_8b2b9b19_fk_staff_cap; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_capability_overrides
    ADD CONSTRAINT staff_capability_ove_capability_id_8b2b9b19_fk_staff_cap FOREIGN KEY (capability_id) REFERENCES public.staff_capabilities_catalog(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: staff_capability_overrides staff_capability_ove_staff_id_d1b4b15e_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_capability_overrides
    ADD CONSTRAINT staff_capability_ove_staff_id_d1b4b15e_fk_hospital_ FOREIGN KEY (staff_id) REFERENCES public.hospital_staff(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: staff_role_capabilities staff_role_capabilit_capability_id_a264d008_fk_staff_cap; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_role_capabilities
    ADD CONSTRAINT staff_role_capabilit_capability_id_a264d008_fk_staff_cap FOREIGN KEY (capability_id) REFERENCES public.staff_capabilities_catalog(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: staff_role_capabilities staff_role_capabilities_role_id_bb650cb4_fk_staff_roles_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.staff_role_capabilities
    ADD CONSTRAINT staff_role_capabilities_role_id_bb650cb4_fk_staff_roles_id FOREIGN KEY (role_id) REFERENCES public.staff_roles(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: student_profiles student_profiles_department_entity_id_8caabb50_fk_universit; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_department_entity_id_8caabb50_fk_universit FOREIGN KEY (department_entity_id) REFERENCES public.university_departments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: student_profiles student_profiles_faculty_entity_id_6e4aca31_fk_universit; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_faculty_entity_id_6e4aca31_fk_universit FOREIGN KEY (faculty_entity_id) REFERENCES public.university_faculties(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: student_profiles student_profiles_hospital_department__f9dbbb22_fk_hospital_; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_hospital_department__f9dbbb22_fk_hospital_ FOREIGN KEY (hospital_department_id) REFERENCES public.hospital_departments(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: student_profiles student_profiles_supervisor_id_791679ac_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_supervisor_id_791679ac_fk_users_id FOREIGN KEY (supervisor_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: student_profiles student_profiles_user_id_37ebcf0c_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.student_profiles
    ADD CONSTRAINT student_profiles_user_id_37ebcf0c_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: university_departments university_departmen_faculty_id_8b44f025_fk_universit; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.university_departments
    ADD CONSTRAINT university_departmen_faculty_id_8b44f025_fk_universit FOREIGN KEY (faculty_id) REFERENCES public.university_faculties(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_group_id_2f3517aa_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_group_id_2f3517aa_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_user_id_f500bee5_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_f500bee5_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissio_permission_id_6d08dcd2_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissio_permission_id_6d08dcd2_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissions_user_id_92473840_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_92473840_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict x9rnf1kzSPOXB07Pz6aD98iHu9iM8xiD4fVTqkMjFM9Ek92H0mNtkBXOKYCZdLw

