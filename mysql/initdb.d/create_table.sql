CREATE TABLE `user_table` (
  `uuid` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pwd` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `firstname` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lastname` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `online` tinyint DEFAULT '1',
  `enable` tinyint DEFAULT '1',
  `summary` varchar(512) COLLATE utf8mb4_unicode_ci NOT NULL,
  `question1` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `question2` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `question3` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`uuid`),
  UNIQUE KEY `idx_user_table_email_pwd` (`email`,`pwd`),
  KEY `idx_users_contact_id` (`contact_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `contact_table` (
  `cid` int NOT NULL AUTO_INCREMENT,
  `owner_uid` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `favorite_uid` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cid`),
  KEY `idx_contact_table_owner_uuid_favorite_uuid` (`owner_uid`,`favorite_uid`),
  KEY `contact_table_ibfk_2` (`favorite_uid`),
  CONSTRAINT `contact_table_ibfk_1` FOREIGN KEY (`owner_uid`) REFERENCES `user_table` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `contact_table_ibfk_2` FOREIGN KEY (`favorite_uid`) REFERENCES `user_table` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `room_table` (
    `room_id` varchar(64)  NOT NULL,
    `uuid` varchar(64)  NOT NULL,
    `aport` integer  DEFAULT 10001,
    `vport` integer  DEFAULT 10002,
    `created_at` timestamp  DEFAULT current_timestamp,
    `updated_at` timestamp  DEFAULT current_timestamp ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`room_id`),
    FOREIGN KEY (`uuid`) REFERENCES `user_table` (`uuid`) ON DELETE CASCADE
);

CREATE INDEX `idx_users_contact_id` ON `user_table` (`contact_id`);