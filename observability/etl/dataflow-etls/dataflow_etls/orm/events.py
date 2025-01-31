import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Union, Optional, Dict, Type
from anchorpy import Event, NamedInstruction

from dataflow_etls.transaction_log_parser import InstructionWithLogs

# IDL event names
MARGINFI_GROUP_CREATE_EVENT = 'MarginfiGroupCreateEvent'
MARGINFI_GROUP_CONFIGURE_EVENT = 'MarginfiGroupConfigureEvent'
LENDING_POOL_BANK_CREATE_EVENT = 'LendingPoolBankCreateEvent'
LENDING_POOL_BANK_CONFIGURE_EVENT = 'LendingPoolBankConfigureEvent'
LENDING_POOL_BANK_ACCRUE_INTEREST_EVENT = 'LendingPoolBankAccrueInterestEvent'
LENDING_POOL_BANK_COLLECT_FEES_EVENT = 'LendingPoolBankCollectFeesEvent'
LENDING_POOL_BANK_HANDLE_BANKRUPTCY_EVENT = 'LendingPoolBankHandleBankruptcyEvent'
MARGINFI_ACCOUNT_CREATE_EVENT = 'MarginfiAccountCreateEvent'
LENDING_ACCOUNT_DEPOSIT_EVENT = 'LendingAccountDepositEvent'
LENDING_ACCOUNT_WITHDRAW_EVENT = 'LendingAccountWithdrawEvent'
LENDING_ACCOUNT_BORROW_EVENT = 'LendingAccountBorrowEvent'
LENDING_ACCOUNT_REPAY_EVENT = 'LendingAccountRepayEvent'
LENDING_ACCOUNT_LIQUIDATE_EVENT = 'LendingAccountLiquidateEvent'


def pascal_to_snake_case(string: str) -> str:
    return re.sub('(?!^)([A-Z]+)', r'_\1', string).lower()


def time_str(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


@dataclass
class RecordBase:
    SCHEMA = ",".join(
        [
            "id:STRING",
            "created_at:TIMESTAMP",
            "idl_version:INTEGER",
            "is_cpi:BOOLEAN",
            "timestamp:TIMESTAMP",
            "signature:STRING",
            "indexing_address:STRING",
        ]
    )

    id: str
    created_at: str
    idl_version: int
    is_cpi: bool
    # call_stack: List[str]
    timestamp: str
    signature: str
    indexing_address: str

    def __init__(self, _event: Event, instruction: InstructionWithLogs, _instruction_args: NamedInstruction):
        self.id = str(uuid.uuid4())
        self.created_at = time_str()
        self.timestamp = time_str(instruction.timestamp)
        self.idl_version = instruction.idl_version
        self.is_cpi = instruction.is_cpi
        # self.call_stack=[str(pk) for pk in instruction.call_stack]
        self.signature = instruction.signature
        self.indexing_address = str(instruction.message.program_id)

    @classmethod
    def get_tag(cls) -> str:
        return cls.__name__


# Event headers

@dataclass
class AccountRecordBase(RecordBase):
    SCHEMA = RecordBase.SCHEMA + "," + ",".join(
        [
            "signer:STRING",
            "marginfi_group:STRING",
            "marginfi_account:STRING",
            "marginfi_account_authority:STRING",
        ]
    )

    signer: Optional[str]
    marginfi_group: str
    marginfi_account: str
    marginfi_account_authority: str

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.signer = str(event.data.header.signer) if event.data.header.signer is not None else None
        self.marginfi_group = str(event.data.header.marginfi_group)
        self.marginfi_account = str(event.data.header.marginfi_account)
        self.marginfi_account_authority = str(event.data.header.marginfi_account_authority)


@dataclass
class GroupRecordBase(RecordBase):
    SCHEMA = RecordBase.SCHEMA + "," + ",".join(
        [
            "signer:STRING",
            "marginfi_group:STRING",
        ]
    )

    signer: Optional[str]
    marginfi_group: str

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.signer = str(event.data.header.signer) if event.data.header.signer is not None else None
        self.marginfi_group = str(event.data.header.marginfi_group)


# Group events


@dataclass
class MarginfiGroupCreateRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)


@dataclass
class MarginfiGroupConfigureRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA + "," + ",".join(
        [
            "admin:STRING",
        ]
    )

    admin: Optional[str]

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.admin = event.data.config.admin


@dataclass
class LendingPoolBankCreateRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA + "," + ",".join(
        [
            "bank:STRING",
            "mint:STRING",
        ]
    )

    bank: str
    mint: str

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.bank = str(event.data.bank)
        self.mint = str(event.data.mint)


@dataclass
class LendingPoolBankConfigureRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA + "," + ",".join(
        [
            "bank:STRING",
            "mint:STRING",
            # "asset_weight_init:NUMERIC",
            # "asset_weight_maint:NUMERIC",
            # "liability_weight_init:NUMERIC",
            # "liability_weight_maint:NUMERIC",
            # "deposit_limit:BIGNUMERIC",
            # "borrow_limit:BIGNUMERIC",
            # "operational_state:STRING",
            # "oracle_setup:STRING",
            # "oracle_keys:STRING",
            # "optimal_utilization_rate:NUMERIC",
            # "plateau_interest_rate:NUMERIC",
            # "max_interest_rate:NUMERIC",
            # "insurance_fee_fixed_apr:NUMERIC",
            # "insurance_ir_fee:NUMERIC",
            # "protocol_fixed_fee_apr:NUMERIC",
            # "protocol_ir_fee:NUMERIC",
        ]
    )

    bank: str
    mint: str

    # todo: config

    # asset_weight_init: Optional[float]
    # asset_weight_maint: Optional[float]
    #
    # liability_weight_init: Optional[float]
    # liability_weight_maint: Optional[float]
    #
    # deposit_limit: Optional[int]
    # borrow_limit: Optional[int]
    #
    # operational_state: Optional[str]
    # oracle_setup: Optional[str]
    # oracle_keys: Optional[str]
    #
    # optimal_utilization_rate: Optional[float]
    # plateau_interest_rate: Optional[float]
    # max_interest_rate: Optional[float]
    #
    # insurance_fee_fixed_apr: Optional[float]
    # insurance_ir_fee: Optional[float]
    # protocol_fixed_fee_apr: Optional[float]
    # protocol_ir_fee: Optional[float]

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.bank = str(event.data.bank)
        self.mint = str(event.data.mint)

        # self.asset_weight_init = event.data.config.asset_weight_init
        # self.asset_weight_maint = event.data.config.asset_weight_maint
        # self.liability_weight_init = event.data.config.liability_weight_init
        # self.liability_weight_maint = event.data.config.liability_weight_maint
        # self.deposit_limit = event.data.config.deposit_limit
        # self.borrow_limit = event.data.config.borrow_limit
        #
        # self.operational_state = str(event.data.config.operational_state)
        # self.oracle_setup = str(event.data.config.oracle.setup) if event.data.config.oracle is not None else None
        # self.oracle_keys = str(event.data.config.oracle.keys) if event.data.config.oracle is not None else None
        #
        # self.optimal_utilization_rate = event.data.config.interest_rate_config.optimal_utilization_rate
        # self.plateau_interest_rate = event.data.config.interest_rate_config.plateau_interest_rate
        # self.max_interest_rate = event.data.config.interest_rate_config.max_interest_rate
        # self.insurance_fee_fixed_apr = event.data.config.interest_rate_config.insurance_fee_fixed_apr
        # self.insurance_ir_fee = event.data.config.interest_rate_config.insurance_ir_fee
        # self.protocol_fixed_fee_apr = event.data.config.interest_rate_config.protocol_fixed_fee_apr
        # self.protocol_ir_fee = event.data.config.interest_rate_config.protocol_ir_fee


@dataclass
class LendingPoolBankAccrueInterestRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA + "," + ",".join(
        [
            "bank:STRING",
            "mint:STRING",
            "delta:BIGNUMERIC",
            "fees_collected:BIGNUMERIC",
            "insurance_collected:BIGNUMERIC",
        ]
    )

    bank: str
    mint: str
    delta: int
    fees_collected: float
    insurance_collected: float

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.bank = str(event.data.bank)
        self.mint = str(event.data.mint)
        self.delta = event.data.delta
        self.fees_collected = event.data.fees_collected
        self.insurance_collected = event.data.insurance_collected


@dataclass
class LendingPoolBankCollectFeesRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA + "," + ",".join(
        [
            "bank:STRING",
            "mint:STRING",
            "group_fees_collected:BIGNUMERIC",
            "group_fees_outstanding:BIGNUMERIC",
            "insurance_fees_collected:BIGNUMERIC",
            "insurance_fees_outstanding:BIGNUMERIC",
        ]
    )

    bank: str
    mint: str
    group_fees_collected: float
    group_fees_outstanding: float
    insurance_fees_collected: float
    insurance_fees_outstanding: float

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.bank = str(event.data.bank)
        self.mint = str(event.data.mint)
        self.group_fees_collected = event.data.group_fees_collected
        self.group_fees_outstanding = event.data.group_fees_outstanding
        self.insurance_fees_collected = event.data.insurance_fees_collected
        self.insurance_fees_outstanding = event.data.insurance_fees_outstanding


@dataclass
class LendingPoolBankHandleBankruptcyRecord(GroupRecordBase):
    SCHEMA = GroupRecordBase.SCHEMA + "," + ",".join(
        [
            "bank:STRING",
            "mint:STRING",
            "bad_debt:BIGNUMERIC",
            "covered_amount:BIGNUMERIC",
            "socialized_amount:BIGNUMERIC",
        ]
    )

    bank: str
    mint: str
    bad_debt: float
    covered_amount: float
    socialized_amount: float

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.bank = str(event.data.bank)
        self.mint = str(event.data.mint)
        self.bad_debt = event.data.bad_debt
        self.covered_amount = event.data.covered_amount
        self.socialized_amount = event.data.socialized_amount


# Account events

@dataclass
class MarginfiAccountCreateRecord(AccountRecordBase):
    SCHEMA = AccountRecordBase.SCHEMA

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)


@dataclass
class LendingAccountChangeLiquidityRecord(AccountRecordBase):
    SCHEMA = AccountRecordBase.SCHEMA + "," + ",".join(
        [
            "operation:STRING",
            "amount:BIGNUMERIC",
            "balance_closed:BOOLEAN"
        ]
    )

    operation: str
    amount: int
    balance_closed: bool

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.operation = event.name.removeprefix("LendingAccount").removesuffix("Event").lower()
        self.amount = event.data.amount
        self.balance_closed = False
        if event.name == LENDING_ACCOUNT_REPAY_EVENT or event.name == LENDING_ACCOUNT_WITHDRAW_EVENT:
            self.balance_closed = event.data.close_balance


@dataclass
class LendingAccountLiquidateRecord(AccountRecordBase):
    SCHEMA = AccountRecordBase.SCHEMA + "," + ",".join(
        [
            "liquidatee_marginfi_account:STRING",
            "liquidatee_marginfi_account_authority:STRING",
            "asset_bank:STRING",
            "asset_mint:STRING",
            "liability_bank:STRING",
            "liability_mint:STRING",
            "liquidatee_pre_health:BIGNUMERIC",
            "liquidatee_post_health:BIGNUMERIC",
            "liquidatee_asset_pre_balance:BIGNUMERIC",
            "liquidatee_liability_pre_balance:BIGNUMERIC",
            "liquidator_asset_pre_balance:BIGNUMERIC",
            "liquidator_liability_pre_balance:BIGNUMERIC",
            "liquidatee_asset_post_balance:BIGNUMERIC",
            "liquidatee_liability_post_balance:BIGNUMERIC",
            "liquidator_asset_post_balance:BIGNUMERIC",
            "liquidator_liability_post_balance:BIGNUMERIC",
        ]
    )

    liquidatee_marginfi_account: str
    liquidatee_marginfi_account_authority: str
    asset_bank: str
    asset_mint: str
    liability_bank: str
    liability_mint: str
    liquidatee_pre_health: float
    liquidatee_post_health: float
    liquidatee_asset_pre_balance: float
    liquidatee_liability_pre_balance: float
    liquidator_asset_pre_balance: float
    liquidator_liability_pre_balance: float
    liquidatee_asset_post_balance: float
    liquidatee_liability_post_balance: float
    liquidator_asset_post_balance: float
    liquidator_liability_post_balance: float

    def __init__(self, event: Event, instruction: InstructionWithLogs, instruction_args: NamedInstruction):
        super().__init__(event, instruction, instruction_args)

        self.liquidatee_marginfi_account = str(event.data.liquidatee_marginfi_account)
        self.liquidatee_marginfi_account_authority = str(event.data.liquidatee_marginfi_account_authority)
        self.asset_bank = str(event.data.asset_bank)
        self.asset_mint = str(event.data.asset_mint)
        self.liability_bank = str(event.data.liability_bank)
        self.liability_mint = str(event.data.liability_mint)
        self.liquidatee_pre_health = event.data.liquidatee_pre_health
        self.liquidatee_post_health = event.data.liquidatee_post_health
        self.liquidatee_asset_pre_balance = event.data.pre_balances.liquidatee_asset_balance
        self.liquidatee_liability_pre_balance = event.data.pre_balances.liquidatee_liability_balance
        self.liquidator_asset_pre_balance = event.data.pre_balances.liquidator_asset_balance
        self.liquidator_liability_pre_balance = event.data.pre_balances.liquidator_liability_balance
        self.liquidatee_asset_post_balance = event.data.post_balances.liquidatee_asset_balance
        self.liquidatee_liability_post_balance = event.data.post_balances.liquidatee_liability_balance
        self.liquidator_asset_post_balance = event.data.post_balances.liquidator_asset_balance
        self.liquidator_liability_post_balance = event.data.post_balances.liquidator_liability_balance


Record = Union[
    MarginfiGroupCreateRecord,
    MarginfiGroupConfigureRecord,
    LendingPoolBankCreateRecord,
    LendingPoolBankConfigureRecord,
    LendingPoolBankAccrueInterestRecord,
    LendingPoolBankCollectFeesRecord,
    LendingPoolBankHandleBankruptcyRecord,
    MarginfiAccountCreateRecord,
    LendingAccountChangeLiquidityRecord,
    LendingAccountLiquidateRecord
]

EVENT_TO_RECORD_TYPE: Dict[str, Type[Record]] = {
    f"{MARGINFI_GROUP_CREATE_EVENT}": MarginfiGroupCreateRecord,
    f"{MARGINFI_GROUP_CONFIGURE_EVENT}": MarginfiGroupConfigureRecord,
    f"{LENDING_POOL_BANK_CREATE_EVENT}": LendingPoolBankCreateRecord,
    f"{LENDING_POOL_BANK_CONFIGURE_EVENT}": LendingPoolBankConfigureRecord,
    f"{LENDING_POOL_BANK_ACCRUE_INTEREST_EVENT}": LendingPoolBankAccrueInterestRecord,
    f"{LENDING_POOL_BANK_COLLECT_FEES_EVENT}": LendingPoolBankCollectFeesRecord,
    f"{LENDING_POOL_BANK_HANDLE_BANKRUPTCY_EVENT}": LendingPoolBankHandleBankruptcyRecord,
    f"{MARGINFI_ACCOUNT_CREATE_EVENT}": MarginfiAccountCreateRecord,
    f"{LENDING_ACCOUNT_DEPOSIT_EVENT}": LendingAccountChangeLiquidityRecord,
    f"{LENDING_ACCOUNT_WITHDRAW_EVENT}": LendingAccountChangeLiquidityRecord,
    f"{LENDING_ACCOUNT_BORROW_EVENT}": LendingAccountChangeLiquidityRecord,
    f"{LENDING_ACCOUNT_REPAY_EVENT}": LendingAccountChangeLiquidityRecord,
    f"{LENDING_ACCOUNT_LIQUIDATE_EVENT}": LendingAccountLiquidateRecord,
}
