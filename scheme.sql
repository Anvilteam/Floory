CREATE TABLE `guilds` (
    `guild` BIGINT NOT NULL,
    `locale` VARCHAR(8) NOT NULL DEFAULT 'ru_RU',
    `logging` VARCHAR(8) NOT NULL DEFAULT 'false',
    `logs-channel` BIGINT NULL DEFAULT NULL,
    `antispam` VARCHAR(8) NOT NULL DEFAULT 'false',
    PRIMARY KEY (`guild`)
) COLLATE='utf8mb4_0900_ai_ci';