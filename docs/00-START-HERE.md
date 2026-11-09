# Start here

Read this page first. It takes 10 minutes.

## What is the challenge?

NASA runs fire experiments on the International Space Station. Fire behaves very differently without gravity, and future habitats on the Moon and Mars will have different air, pressure and gravity than Earth. The results are public in NASA's PSI repository, but they are spread across experiment pages, papers and plots. An engineer who asks "is my cabin design covered by tests?" has to read for days.

## What are we building?

**FlameLens.** The engineer types in their habitat: oxygen %, pressure, airflow, fuel, gravity. FlameLens answers three questions:

| Question | Our feature |
|---|---|
| Is my design backed by experiments? | **Evidence case**: each condition marked Supported, Weak or No evidence, with run IDs |
| What should we test next? | **Run this next**: the experiment that closes the most gaps |
| What can I change to be safer? | **Safer options**: nearest tested conditions with less oxygen |

Behind it: a ranker that scores experiments against the habitat, charts for airflow, smoke vs dust and cool flames, and an AI that explains results but must cite real runs.

See the picture: the [dashboard mockup](links.md) shows all of this.

## The constraint that shapes everything

**The dataset is not available until 13 Nov.** So before the hackathon we prepare: plan, designs, documents, accounts, research notes, placeholder data, and a way of working. We build the product in the 48 hours.

## What you do now

1. Open [02 Team roles](02-team-roles.md) and write your name next to a role (the team agrees roles in the group chat first).
2. Open your role file in [roles/](roles). It lists tasks with due dates and a "done when" for each.
3. Do the **everyone** tasks below.
4. Tick your tasks in [../TASKS.md](../TASKS.md) as you finish them.

### Everyone, by Tuesday 10 Nov

- [ ] Read this page, the [project brief](01-project-brief.md) and [working agreements](08-working-agreements.md)
- [ ] Open the interactive [dashboard mockup](links.md) and try the three tabs: Evidence case, Run this next, Safer options
- [ ] Have a GitHub account, accept the repo invitation, and clone the repo
- [ ] Run `python scripts/check_env.py` and fix anything marked MISSING for your role
- [ ] Join the team chat and share your availability for 13–14 Nov (sleep shifts are planned from this)
- [ ] Write down any questions about the plan in the chat

## Words you will hear

| Word | Meaning |
|---|---|
| PSI | Physical Sciences Informatics, NASA's open repository of experiment data |
| Run | One experiment test with its conditions and result |
| Investigation | A named experiment campaign such as BASS or SAME that contains many runs |
| Pillar | Prevention, Detection or Suppression: the three groups of investigations |
| O₂ partial pressure | Pressure × oxygen fraction. Earth air is about 3.1 psi. A better measure of fire risk than oxygen % alone |
| LOC | Limiting oxygen concentration: the lowest oxygen where a flame still burns |
| Placeholder | Fake sample data used to build the app before real data arrives. Always labelled |
| Verifier | Code that removes any AI claim not backed by a real run ID |

More detail: the interactive [FlameLens Explained](links.md) page.

## If you are stuck

Ask in the team chat. Say what you tried. The tech lead (role A) unblocks tooling, role F unblocks anything about rules and submission.
