# Astra prompt routing

## Goal
Apply the explicit user correction: image and Seedance video prompt authoring use gpt-6-astra instead of gpt-5.6-sol.

## Scope
Change the three creative dispatch routes, preserve xhigh effort, Luna execution/QC/edit routes and exact spawn approvals. Current conversation remains the sole owner; image_gen remains the still generator and Seedance 2.0 the video generator. No submitted job or historical project is migrated. Update active runtime text and current production project routing metadata.

## Acceptance
- All image_creator_01/02 and seedance:prompting routes resolve to Astra xhigh.
- Production and flow remain Luna high; no spawn permission is added.
- Generated prompts and workflow output contain no obsolete Sol phase label.
- Unit tests, source/live deployment parity and isolated GitHub sync pass.
- This route-only release does not claim real video-cycle completion.
