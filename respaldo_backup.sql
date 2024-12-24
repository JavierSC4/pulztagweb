--
-- PostgreSQL database dump
--

-- Dumped from database version 14.14 (Homebrew)
-- Dumped by pg_dump version 14.15 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO javiersc;

--
-- Name: bodegas; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.bodegas (
    id integer NOT NULL,
    id_bodega character varying(10) NOT NULL,
    nombre character varying(255) NOT NULL,
    ubicacion character varying(255),
    notas text,
    fecha_creacion timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    uuid character varying(36) NOT NULL
);


ALTER TABLE public.bodegas OWNER TO javiersc;

--
-- Name: bodegas_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.bodegas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bodegas_id_seq OWNER TO javiersc;

--
-- Name: bodegas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.bodegas_id_seq OWNED BY public.bodegas.id;


--
-- Name: cajas; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.cajas (
    id integer NOT NULL,
    id_caja character varying(10) NOT NULL,
    nombre character varying(255) NOT NULL,
    categoria character varying(255),
    notas text,
    fecha_creacion timestamp without time zone NOT NULL,
    bodega_id integer NOT NULL,
    uuid character varying(36) NOT NULL
);


ALTER TABLE public.cajas OWNER TO javiersc;

--
-- Name: cajas_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.cajas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cajas_id_seq OWNER TO javiersc;

--
-- Name: cajas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.cajas_id_seq OWNED BY public.cajas.id;


--
-- Name: daily_views; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.daily_views (
    id integer NOT NULL,
    item_id integer NOT NULL,
    date date NOT NULL,
    views integer NOT NULL
);


ALTER TABLE public.daily_views OWNER TO javiersc;

--
-- Name: daily_views_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.daily_views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.daily_views_id_seq OWNER TO javiersc;

--
-- Name: daily_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.daily_views_id_seq OWNED BY public.daily_views.id;


--
-- Name: dashboard_items; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.dashboard_items (
    id integer NOT NULL,
    uuid character varying(36) NOT NULL,
    name character varying(100) NOT NULL,
    item_type character varying(50) NOT NULL,
    user_id integer NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.dashboard_items OWNER TO javiersc;

--
-- Name: dashboard_items_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.dashboard_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dashboard_items_id_seq OWNER TO javiersc;

--
-- Name: dashboard_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.dashboard_items_id_seq OWNED BY public.dashboard_items.id;


--
-- Name: productos; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.productos (
    id integer NOT NULL,
    id_producto character varying(10) NOT NULL,
    nombre character varying(255) NOT NULL,
    descripcion text,
    cantidad integer NOT NULL,
    categoria character varying(100),
    subcategoria character varying(100),
    fecha_creacion timestamp without time zone NOT NULL,
    caja_id integer NOT NULL,
    uuid character varying(36) NOT NULL,
    notas text
);


ALTER TABLE public.productos OWNER TO javiersc;

--
-- Name: productos_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.productos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.productos_id_seq OWNER TO javiersc;

--
-- Name: productos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.productos_id_seq OWNED BY public.productos.id;


--
-- Name: pulzcards; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.pulzcards (
    id integer NOT NULL,
    card_name character varying(100) NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    organization character varying(100) NOT NULL,
    "position" character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    email character varying(120) NOT NULL,
    website character varying(200) NOT NULL,
    address character varying(200) NOT NULL,
    card_id character varying(36) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    image_file character varying(100),
    template character varying(20) NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.pulzcards OWNER TO javiersc;

--
-- Name: pulzcards_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.pulzcards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pulzcards_id_seq OWNER TO javiersc;

--
-- Name: pulzcards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.pulzcards_id_seq OWNED BY public.pulzcards.id;


--
-- Name: survey_responses; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.survey_responses (
    id integer NOT NULL,
    item_id integer NOT NULL,
    rating integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.survey_responses OWNER TO javiersc;

--
-- Name: survey_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.survey_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.survey_responses_id_seq OWNER TO javiersc;

--
-- Name: survey_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.survey_responses_id_seq OWNED BY public.survey_responses.id;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.tags (
    id integer NOT NULL,
    tag_name character varying(100) NOT NULL,
    redirect_url character varying(200) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    tag_id character varying(36) NOT NULL,
    vistas integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.tags OWNER TO javiersc;

--
-- Name: tags_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tags_id_seq OWNER TO javiersc;

--
-- Name: tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.tags_id_seq OWNED BY public.tags.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: javiersc
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(150) NOT NULL,
    email character varying(120) NOT NULL,
    password character varying(60),
    is_admin boolean,
    is_verified boolean,
    must_change_password boolean
);


ALTER TABLE public.users OWNER TO javiersc;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: javiersc
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO javiersc;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: javiersc
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: bodegas id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.bodegas ALTER COLUMN id SET DEFAULT nextval('public.bodegas_id_seq'::regclass);


--
-- Name: cajas id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.cajas ALTER COLUMN id SET DEFAULT nextval('public.cajas_id_seq'::regclass);


--
-- Name: daily_views id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.daily_views ALTER COLUMN id SET DEFAULT nextval('public.daily_views_id_seq'::regclass);


--
-- Name: dashboard_items id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.dashboard_items ALTER COLUMN id SET DEFAULT nextval('public.dashboard_items_id_seq'::regclass);


--
-- Name: productos id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.productos ALTER COLUMN id SET DEFAULT nextval('public.productos_id_seq'::regclass);


--
-- Name: pulzcards id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.pulzcards ALTER COLUMN id SET DEFAULT nextval('public.pulzcards_id_seq'::regclass);


--
-- Name: survey_responses id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.survey_responses ALTER COLUMN id SET DEFAULT nextval('public.survey_responses_id_seq'::regclass);


--
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.tags ALTER COLUMN id SET DEFAULT nextval('public.tags_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: bodegas; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.bodegas (id, id_bodega, nombre, ubicacion, notas, fecha_creacion, user_id, uuid) FROM stdin;
\.


--
-- Data for Name: cajas; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.cajas (id, id_caja, nombre, categoria, notas, fecha_creacion, bodega_id, uuid) FROM stdin;
\.


--
-- Data for Name: daily_views; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.daily_views (id, item_id, date, views) FROM stdin;
\.


--
-- Data for Name: dashboard_items; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.dashboard_items (id, uuid, name, item_type, user_id, created_at) FROM stdin;
28	88671cbe-5794-4493-a28d-34546073046a	Encuesta Sony	Evaluación de Clientes	1	2024-12-24 18:09:52.487478
29	866cb7ce-e67b-477f-9410-356595c4bf49	rrr	Evaluación de Clientes	1	2024-12-24 18:21:29.675803
\.


--
-- Data for Name: productos; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.productos (id, id_producto, nombre, descripcion, cantidad, categoria, subcategoria, fecha_creacion, caja_id, uuid, notas) FROM stdin;
\.


--
-- Data for Name: pulzcards; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.pulzcards (id, card_name, first_name, last_name, organization, "position", phone, email, website, address, card_id, created_at, image_file, template, user_id) FROM stdin;
1	Etiqueta	Javier	Salinas	CO	CO	+56962411963	contacto@pulztag.com	https://pulztag.com	Providencia	71b6490b-6ef7-4745-ab30-f5eb4c9ec1f1	2024-12-24 15:20:32.761755	24f8014ce63e4288a8f0ac563c72b7d9_81MRsuj0ULL._AC_SL1500_.jpg	template1	1
\.


--
-- Data for Name: survey_responses; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.survey_responses (id, item_id, rating, "timestamp") FROM stdin;
23	28	1	2024-12-24 15:10:10.289977
24	29	5	2024-12-24 15:25:20.303601
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.tags (id, tag_name, redirect_url, created_at, tag_id, vistas, user_id) FROM stdin;
1	Etiqueta jumbo	https://www.jumbo.cl	2024-12-24 15:18:22.000276	f702dcb9-3578-47d5-870b-dd6afdc6a11a	0	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: javiersc
--

COPY public.users (id, username, email, password, is_admin, is_verified, must_change_password) FROM stdin;
2	Javito8	javiersalinas_@hotmail.com	$2b$12$KOQxPM/UHtfn5HKf7weqBuvjw5i2i.hiiaDhL1ymufX309uaLtBc.	f	f	f
3	Prueba 2	javass_8@hotmail.com	$2b$12$Q7Jg.KvjMr5K5kB3PlW9P.hpjx7AoN/OcecBK.j5a/xKK0sSj7bL.	f	f	f
1	admin	contacto@pulztag.com	$2b$12$hOF857KuW.gmEKbUSq77ROQ28yMvMqdWjOYnBryEzoguq4WAVAOpe	t	f	f
\.


--
-- Name: bodegas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.bodegas_id_seq', 1, false);


--
-- Name: cajas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.cajas_id_seq', 1, false);


--
-- Name: daily_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.daily_views_id_seq', 1, false);


--
-- Name: dashboard_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.dashboard_items_id_seq', 29, true);


--
-- Name: productos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.productos_id_seq', 1, false);


--
-- Name: pulzcards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.pulzcards_id_seq', 1, true);


--
-- Name: survey_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.survey_responses_id_seq', 24, true);


--
-- Name: tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.tags_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: javiersc
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bodegas bodegas_id_bodega_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.bodegas
    ADD CONSTRAINT bodegas_id_bodega_key UNIQUE (id_bodega);


--
-- Name: bodegas bodegas_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.bodegas
    ADD CONSTRAINT bodegas_pkey PRIMARY KEY (id);


--
-- Name: bodegas bodegas_uuid_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.bodegas
    ADD CONSTRAINT bodegas_uuid_key UNIQUE (uuid);


--
-- Name: cajas cajas_id_caja_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.cajas
    ADD CONSTRAINT cajas_id_caja_key UNIQUE (id_caja);


--
-- Name: cajas cajas_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.cajas
    ADD CONSTRAINT cajas_pkey PRIMARY KEY (id);


--
-- Name: cajas cajas_uuid_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.cajas
    ADD CONSTRAINT cajas_uuid_key UNIQUE (uuid);


--
-- Name: daily_views daily_views_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.daily_views
    ADD CONSTRAINT daily_views_pkey PRIMARY KEY (id);


--
-- Name: dashboard_items dashboard_items_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.dashboard_items
    ADD CONSTRAINT dashboard_items_pkey PRIMARY KEY (id);


--
-- Name: dashboard_items dashboard_items_uuid_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.dashboard_items
    ADD CONSTRAINT dashboard_items_uuid_key UNIQUE (uuid);


--
-- Name: productos productos_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id);


--
-- Name: productos productos_uuid_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_uuid_key UNIQUE (uuid);


--
-- Name: pulzcards pulzcards_card_id_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.pulzcards
    ADD CONSTRAINT pulzcards_card_id_key UNIQUE (card_id);


--
-- Name: pulzcards pulzcards_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.pulzcards
    ADD CONSTRAINT pulzcards_pkey PRIMARY KEY (id);


--
-- Name: survey_responses survey_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_pkey PRIMARY KEY (id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: tags tags_tag_id_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_tag_id_key UNIQUE (tag_id);


--
-- Name: daily_views unique_item_date; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.daily_views
    ADD CONSTRAINT unique_item_date UNIQUE (item_id, date);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: bodegas bodegas_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.bodegas
    ADD CONSTRAINT bodegas_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: cajas cajas_bodega_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.cajas
    ADD CONSTRAINT cajas_bodega_id_fkey FOREIGN KEY (bodega_id) REFERENCES public.bodegas(id) ON DELETE CASCADE;


--
-- Name: daily_views daily_views_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.daily_views
    ADD CONSTRAINT daily_views_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.dashboard_items(id);


--
-- Name: dashboard_items dashboard_items_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.dashboard_items
    ADD CONSTRAINT dashboard_items_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: productos productos_caja_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_caja_id_fkey FOREIGN KEY (caja_id) REFERENCES public.cajas(id) ON DELETE CASCADE;


--
-- Name: pulzcards pulzcards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.pulzcards
    ADD CONSTRAINT pulzcards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: survey_responses survey_responses_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.survey_responses
    ADD CONSTRAINT survey_responses_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.dashboard_items(id);


--
-- Name: tags tags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: javiersc
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

