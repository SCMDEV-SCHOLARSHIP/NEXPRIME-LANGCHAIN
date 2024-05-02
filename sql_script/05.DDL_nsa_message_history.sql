-- Table: nexprimescmmgr.nsa_message_history

-- DROP TABLE IF EXISTS nexprimescmmgr.nsa_message_history;

CREATE TABLE IF NOT EXISTS nexprimescmmgr.nsa_message_history
(
    message_id serial NOT NULL,
    user_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
    sender character varying(5) COLLATE pg_catalog."default" NOT NULL,
    content varchar COLLATE pg_catalog."default" NOT NULL,
    sources varchar[] COLLATE pg_catalog."default",
    create_datetime timestamp with time zone NOT NULL,
    create_user_id character varying COLLATE pg_catalog."default" NOT NULL,
    modified_datetime timestamp with time zone NOT NULL,
    modified_user_id character varying COLLATE pg_catalog."default" NOT NULL,
    delete_yn boolean NOT NULL,
    CONSTRAINT nsa_message_pkey PRIMARY KEY (message_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS nexprimescmmgr.nsa_message_history
    OWNER to nexprimescmmgr;
