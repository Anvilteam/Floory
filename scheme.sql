CREATE TABLE `guilds` (
    `guild` BIGINT NOT NULL,
    `logging` VARCHAR(8) NOT NULL DEFAULT 'false',
    `logs-channel` BIGINT NULL DEFAULT NULL,
    `auto-role` BIGINT NULL DEFAULT NULL,
    PRIMARY KEY (`guild`)
);
