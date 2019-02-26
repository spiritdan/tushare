CREATE SCHEMA `security` ;
USE `security`;

CREATE TABLE `stock_list` (
  `stock_list_id` int(11) unsigned NOT NULL,
  `code` varchar(9) NOT NULL,
  `name` varchar(8) NOT NULL,
  `status` tinyint(1) unsigned NOT NULL COMMENT 'ipo: 1;\\nactive: 2;\\nsuspended: 3;\\ndelisted: 4.',
  `list_date` date NOT NULL,
  CONSTRAINT `pk_stock_list` PRIMARY KEY (`stock_list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `trade_history` (
  `trade_history_id` int(11) unsigned NOT NULL,
  `stock_list_id` int(11) unsigned NOT NULL,
  `trade_date` date NOT NULL,
  `open_price` float unsigned NOT NULL,
  `high_price` float unsigned NOT NULL,
  `low_price` float unsigned NOT NULL,
  `close_price` float unsigned NOT NULL,
  `percentile25_price` float unsigned DEFAULT NULL COMMENT 'calculated from table ''trade_detail''.',
  `weighted_average_price` float unsigned DEFAULT NULL COMMENT '1. calculated from table ''trade_detail''.\n2. weighted by volumn.',
  `percentile75_price` float unsigned DEFAULT NULL COMMENT 'calculated from table ''trade_detail''.',
  `volumn` float unsigned NOT NULL,
  `amount` float unsigned NOT NULL,
  CONSTRAINT `pk_trade_history` PRIMARY KEY (`trade_history_id`),
  CONSTRAINT `fk_trade_history` FOREIGN KEY (`stock_list_id`) REFERENCES stock_list(`stock_list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `trade_detail` (
  `trade_detail_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `trade_history_id` int(10) unsigned NOT NULL,
  `trade_time` time NOT NULL,
  `price` float NOT NULL,
  `volumn` float NOT NULL,
  `initiator` tinyint(4) NOT NULL COMMENT 'buyer: 1\nseller: -1\nboth: 0',
  CONSTRAINT `pk_trade_detail` PRIMARY KEY (`trade_detail_id`),
  CONSTRAINT `fk_trade_detail` FOREIGN KEY (`trade_history_id`) REFERENCES trade_history(`trade_history_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `right` (
  `right_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `stock_list_id` int(10) unsigned NOT NULL,
  `exright_date` date NOT NULL,
  `cash_dividend` float unsigned DEFAULT NULL,
  `share_dividend` float unsigned DEFAULT NULL,
  `converted_share` float unsigned DEFAULT NULL,
  `share_placement` float unsigned DEFAULT NULL,
  `placement_price` float unsigned DEFAULT NULL,
  CONSTRAINT `pk_right` PRIMARY KEY (`right_id`),
  CONSTRAINT `fk_right` FOREIGN KEY (`stock_list_id`) REFERENCES stock_list(`stock_list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `financial_report` (
  `financial_report_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `stock_list_id` int(10) unsigned NOT NULL,
  `report_date` date NOT NULL,
  `holder_count` int(10) unsigned NOT NULL,
  `total_asset` float unsigned NOT NULL,
  `total_liability` float unsigned NOT NULL,
  `capital` float unsigned NOT NULL,
  `equity` float NOT NULL,
  `net_profit` float NOT NULL,
  `net_operation_cash_flow` float NOT NULL,
  `net_investment_cash_flow` float NOT NULL,
  `net_financing_cash_flow` float NOT NULL,
  CONSTRAINT `pk_financial_report` PRIMARY KEY (`financial_report_id`),
  CONSTRAINT `fk_financial_report` FOREIGN KEY (`stock_list_id`) REFERENCES stock_list(`stock_list_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
