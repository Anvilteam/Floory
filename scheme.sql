CREATE TABLE `guilds` (
    `guild` BIGINT NOT NULL,
    `locale` VARCHAR(8) NOT NULL DEFAULT 'ru_RU',
    `logging` VARCHAR(8) NOT NULL DEFAULT 'false',
    `logs-channel` BIGINT NULL DEFAULT NULL,
    PRIMARY KEY (`guild`)
);
