-- Table: nexprimescmmgr.nsa_llm_model

-- DROP TABLE IF EXISTS nexprimescmmgr.nsa_llm_model;

CREATE TABLE IF NOT EXISTS nexprimescmmgr.nsa_llm_model
(
    llm_id integer NOT NULL DEFAULT nextval('nsa_llm_model_llm_id_seq'::regclass),
    llm_type character varying(200) COLLATE pg_catalog."default" NOT NULL,
    llm_name character varying(200) COLLATE pg_catalog."default" NOT NULL,
    inference_server_url character varying(4096) COLLATE pg_catalog."default",
    max_new_tokens integer,
    top_k integer,
    top_p double precision,
    typical_p double precision,
    temperature double precision,
    repetition_penalty double precision,
    streaming boolean,
    api_key character varying(500) COLLATE pg_catalog."default",
    create_datetime timestamp with time zone NOT NULL,
    create_user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    modified_datetime timestamp with time zone NOT NULL,
    modified_user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    delete_yn boolean NOT NULL,
    CONSTRAINT nsa_llm_model_pkey PRIMARY KEY (llm_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS nexprimescmmgr.nsa_llm_model
    OWNER to nexprimescmmgr;