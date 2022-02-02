CREATE TABLE `guilds` (
    `guild` BIGINT NOT NULL,
    `locale` VARCHAR(8) NOT NULL DEFAULT 'ru_RU',
    `logging` VARCHAR(8) NOT NULL DEFAULT 'false',
    `logs-channel` BIGINT NULL DEFAULT NULL,
    `news` VARCHAR(8) NOT NULL DEFAULT 'false',
    `news-channel` BIGINT NULL DEFAULT NULL,
    PRIMARY KEY (`guild`)
) COLLATE='utf8mb4_0900_ai_ci';