CREATE TABLE  IF NOT EXISTS Users(
    id bigint,
    display_name text,
    about_me text,
    age bigint,
    creation_date timestamptz,
    last_access_date timestamptz,
    location text,
    reputation bigint,
    up_votes bigint,
    down_votes bigint,
    views bigint,
    profile_image_url text,
    website_url text,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE  IF NOT EXISTS Questions (
    Id bigint,
    OwnerUserId bigint,
    CreationDate timestamptz,
    Score bigint,
    Title text,
    Body text,
    CONSTRAINT questions_pkey PRIMARY KEY (Id),
    CONSTRAINT questions_fkey FOREIGN KEY (OwnerUserId) REFERENCES Users(id)
);

CREATE table IF NOT EXISTS Answers(
    Id bigint,
    OwnerUserId bigint,
    CreationDate timestamptz,
    ParentId bigint,
    Score bigint,
    Body text,
    CONSTRAINT answers_pkey PRIMARY KEY (Id),
    CONSTRAINT answers_user_fkey FOREIGN KEY (OwnerUserId) REFERENCES Users(id),
    CONSTRAINT answers_question_fkey FOREIGN KEY (ParentId) REFERENCES Questions(Id)
);

CREATE TABLE  IF NOT EXISTS Tags(
    id bigint,
    tag text,
    CONSTRAINT tags_question_fkey FOREIGN KEY (id) REFERENCES Questions(Id)
);


\copy Users from 'Users.csv' DELIMITER ',' CSV HEADER;
\copy Questions from 'Questions.csv' DELIMITER ',' CSV HEADER ;
\copy Answers from 'Answers.csv' DELIMITER ',' CSV HEADER;
\copy Tags from 'Tags.csv'  DELIMITER ',' CSV HEADER;

CREATE INDEX idx1 ON answers(parentid);
CREATE INDEX idx2 ON tags(tag);


