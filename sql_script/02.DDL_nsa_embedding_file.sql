-- Table: nexprimescmmgr.nsa_embedding_file

-- DROP TABLE IF EXISTS nexprimescmmgr.nsa_embedding_file;

CREATE TABLE IF NOT EXISTS nexprimescmmgr.nsa_embedding_file
(
    uuid uuid NOT NULL,
    file_path character varying(255) COLLATE pg_catalog."default" NOT NULL,
    file_name character varying(100) COLLATE pg_catalog."default" NOT NULL,
    file_extension character varying(10) COLLATE pg_catalog."default",
    create_datetime timestamp with time zone NOT NULL,
    create_user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    modified_datetime timestamp with time zone NOT NULL,
    modified_user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    delete_yn boolean NOT NULL,
    CONSTRAINT nsa_embedding_file_pkey PRIMARY KEY (uuid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS nexprimescmmgr.nsa_embedding_file
    OWNER to nexprimescmmgr;