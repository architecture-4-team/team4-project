CREATE TABLE IF NOT EXISTS `user_table` (
    `uuid` varchar(64)  NOT NULL ,
    `contact_id` varchar(256)  NOT NULL ,
    `email` varchar(64)  NOT NULL ,
    `pwd` varchar(64)  NOT NULL ,
    `firstname` varchar(32)  NOT NULL ,
    `lastname` varchar(32)  NOT NULL ,
    `ip` varchar(32)  NOT NULL ,
    `status` tinyint  DEFAULT 1,
    `summary` varchar(512) NOT NULL,
    `question1` varchar(16) NOT NULL,
    `question2` varchar(16) NOT NULL,
    `question3` varchar(16) NOT NULL,
    `created_at` timestamp  DEFAULT current_timestamp,
    `updated_at` timestamp  DEFAULT current_timestamp,
    PRIMARY KEY (`uuid`)
);

CREATE TABLE `contact_table` (
    `owner_uuid` varchar(64)  NOT NULL,
    `favorite_uuid` varchar(64)  NOT NULL,
    `nickname` varchar(32)  NOT NULL,
    `created_at` timestamp  DEFAULT current_timestamp,
    `updated_at` timestamp  DEFAULT current_timestamp ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`owner_uuid`) REFERENCES `user_table` (`uuid`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `room_table` (
    `room_id` varchar(64)  NOT NULL ,
    `uuid` varchar(64)  NOT NULL ,
    `aport` integer  DEFAULT 10001,
    `vport` integer  DEFAULT 10002,
    `created_at` timestamp  DEFAULT current_timestamp,
    `updated_at` timestamp  DEFAULT current_timestamp,
    PRIMARY KEY (`room_id`),
    FOREIGN KEY (`uuid`) REFERENCES `user_table` (`uuid`) ON DELETE CASCADE
);

CREATE INDEX `idx_users_contact_id` ON `user_table` (`contact_id`);