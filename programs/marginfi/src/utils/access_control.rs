use crate::{check, prelude::*, state::marginfi_group::MarginfiGroup};
use anchor_lang::prelude::AccountLoader;

pub fn group_paused(marginfi_group: &AccountLoader<MarginfiGroup>) -> MarginfiResult {
    check!(!marginfi_group.load()?.paused, MarginfiError::GroupPaused);

    Ok(())
}
