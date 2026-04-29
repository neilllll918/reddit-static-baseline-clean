\# Reddit Static Network Baseline



This repository contains a small prototype pipeline for preparing Reddit comment data for static-network opinion simulation.



\## Current Progress



This version does not run LLM agents. The original LLM update requires an OpenAI API key.



Instead, this repo provides a numeric baseline prototype using Reddit immigration-related comments.



\## Pipeline



1\. Stream Reddit comments from `RC\_2019-04.zst` without downloading the full 15GB file.

2\. Filter comments from the `politics` subreddit related to immigration, border, asylum, refugee, deport, and migrant.

3\. Convert comments into 50 Reddit agents.

4\. Manually label each agent's `initial\_belief` from -2 to 2 based on the question:



&#x20;  \*\*Should the U.S. adopt stricter immigration policies?\*\*



5\. Place the 50 agents into three static network structures:

&#x20;  - small-world network

&#x20;  - scale-free network

&#x20;  - random graph



6\. Run a DeGroot-style numeric baseline.

7\. Compute:

&#x20;  - polarization

&#x20;  - global disagreement

&#x20;  - neighbor correlation



\## Files



\- `stream\_reddit\_topic\_sample.py`: stream and filter Reddit comments by topic

\- `create\_reddit\_agents.py`: convert Reddit comments into 50 agents

\- `run\_static\_baseline.py`: run static network numeric baseline

\- `reddit\_agents\_anonymized.csv`: 50 anonymized Reddit agents with manually labeled initial beliefs

\- `static\_baseline\_results.csv`: metric values over simulation steps

\- `polarization.png`

\- `global\_disagreement.png`

\- `neighbor\_correlation.png`



\## Notes



Large raw Reddit files, virtual environments, API keys, and checkpoints are not included.

