-- Table: nexprimescmmgr.nsa_refresh_token

-- DROP TABLE IF EXISTS nexprimescmmgr.nsa_refresh_token;

CREATE TABLE IF NOT EXISTS nexprimescmmgr.nsa_refresh_token
(
    user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    refresh_token character varying(4096) COLLATE pg_catalog."default" NOT NULL,
    create_datetime timestamp with time zone NOT NULL,
    create_user_id character varying COLLATE pg_catalog."default" NOT NULL,
    modified_datetime timestamp with time zone NOT NULL,
    modified_user_id character varying COLLATE pg_catalog."default" NOT NULL,
    delete_yn boolean NOT NULL,
    CONSTRAINT nsa_user_token_pkey PRIMARY KEY (user_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS nexprimescmmgr.nsa_refresh_token
    OWNER to nexprimescmmgr;
