# Review decisions

This directory stores evidence-linked decisions for imported metadata. A review
decision records which checks passed, failed, or remain unresolved; it does not
change the imported record by itself.

Files whose `reviewer_id` identifies an automated source audit are preliminary.
Even when every source check passes, promotion remains blocked until a named
human reviewer approves the decision under the verification policy.
