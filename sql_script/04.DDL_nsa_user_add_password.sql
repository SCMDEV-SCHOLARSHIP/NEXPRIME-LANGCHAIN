drop table nsa_user;
-- Table: nexprimescmmgr.nsa_user

-- DROP TABLE IF EXISTS nexprimescmmgr.nsa_user;

CREATE TABLE IF NOT EXISTS nexprimescmmgr.nsa_user
(
    user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    user_name character varying(100) COLLATE pg_catalog."default",
    user_email character varying(100) COLLATE pg_catalog."default" NOT NULL,
    user_password character varying(500) COLLATE pg_catalog."default" NOT NULL,
    create_datetime timestamp with time zone NOT NULL,
    create_user_id character varying COLLATE pg_catalog."default" NOT NULL,
    modified_datetime timestamp with time zone NOT NULL,
    modified_user_id character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT nsa_user_pkey PRIMARY KEY (user_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS nexprimescmmgr.nsa_user
    OWNER to nexprimescmmgr;