![LinkdAPI Favicon](https://linkdapi.com/favicon.ico)

# LinkdAPI Python - Unofficial LinkedIn API

[![PyPI Version](https://img.shields.io/pypi/v/linkdapi)](https://pypi.org/project/linkdapi/)
[![Python Versions](https://img.shields.io/pypi/pyversions/linkdapi)](https://pypi.org/project/linkdapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/linkdapi?style=social)](https://x.com/l1nkdapi)

🔑 **[Get Your API Key](https://linkdapi.com/?p=signup)** (100 free credits) • 📖 **[Full Documentation](https://linkdapi.com/docs)**

A lightweight Python wrapper for [LinkdAPI](https://linkdapi.com) — the most advanced **unofficial LinkedIn API** you’ll ever find. Instead of relying on brittle scrapers or search engine hacks, **LinkdAPI** connects straight to LinkedIn’s own mobile and web endpoints. That means you get access to real-time data with unmatched **reliability**, **stability**, and **scalability** — perfect for developers, analysts, and anyone building tools that tap into LinkedIn at scale.

---

## Why LinkdAPI?

- We **do not rely on search engines** or SERP scraping – all data is retrieved **directly from LinkedIn.**
- Built for **scale, stability, and accuracy** using direct endpoints.
- Ideal for **automation**, **data extraction**, **reverse lookup**, and **lead generation**.

![LinkdAPI Hero](https://linkdapi.com/hero.jpg)

## Why LinkdAPI Beats Alternatives

| Feature | LinkdAPI | SerpAPI | Scraping |
|---------|----------|---------|----------|
| **Direct LinkedIn Access** | ✅ Yes | ❌ No | ❌ No |
| **No Proxy Management** | ✅ Yes | ❌ No | ❌ No |
| **No Cookies Management** | ✅ Yes | ❌ No | ❌ No |
| **Structured JSON Data** | ✅ Yes | ❌ HTML | ✅ Yes |
| **Scalability** | ✅ Built for scale | ❌ Rate-limited | ❌ Manual effort |
| **Pricing Transparency**    | ✅ Clear pricing tiers  | ✅ Pay-per-request     | ❌ Hidden costs (proxies, CAPTCHAs) |
| **API Reliability**         | ✅ High uptime         | ✅ Good                | ❌ Unstable (blocks)   |
| **Automation-Friendly**     | ✅ Full automation      | ✅ Partial             | ❌ Manual work needed  |
| **Support & Documentation**| ✅ Dedicated support   | ✅ Good docs           | ❌ Community-based     |
| **Anti-Blocking**           | ✅ Built-in evasion     | ❌ N/A                 | ❌ High risk           |
---

## 📦 Installation

Install with pip:

```bash
pip install linkdapi
```

---

## 💻 Usage

```python
from linkdapi import LinkdAPI

client = LinkdAPI("your_api_key")

# Get profile overview
profile = client.get_profile_overview("ryanroslansky")
print(profile)
```
# 📚 LinkdAPI Python - Available Methods & Usage

all available methods in the `LinkdAPI` class.


---

## 🔹 Profiles Data
```python
get_profile_overview(username)
get_profile_details(urn)
get_contact_info(username)
get_full_experience(urn)
get_certifications(urn)
get_education(urn)
get_skills(urn)
get_social_matrix(username)
get_recommendations(urn)
get_similar_profiles(urn)
get_profile_about(urn)
get_profile_reactions(urn, cursor='')
```

## 🔹 Companies Data
```python
company_name_lookup(query)
get_company_info(company_id=None, name=None)
get_similar_companies(company_id)
get_company_employees_data(company_id)
```

## 🔹 Jobs Data
```python
search_jobs(
  keyword=None,
  location=None,
  geo_id=None,
  company_ids=None,
  job_types=None,
  experience=None,
  regions=None,
  time_posted='any',
  salary=None,
  work_arrangement=None,
  start=0
)
get_job_details(job_id)
get_similar_jobs(job_id)
get_people_also_viewed_jobs(job_id)
```

## 🔹 Posts Data
```python
get_featured_posts(urn)
get_all_posts(urn, cursor='', start=0)
get_post_info(urn)
get_post_comments(urn, start=0, count=10, cursor='')
get_post_likes(urn, start=0)
```

## 🔹 Comments Data
```python
get_all_comments(urn, cursor='')
get_comment_likes(urns, start=0)
```

## 🔹 Geos Lookup
```python
geo_name_lookup(query)
```

## 🔹 Skills & Titles Lookup
```python
title_skills_lookup(query)
```

## 🔹 System
```python
get_service_status()
```
### More endpoints to come soon...


## 📈 Best Use Cases

- **LinkedIn Data Extractor**  
  Easily automate the process of collecting LinkedIn data at scale—ideal for research, lead generation, and insights.
- **LinkedIn Profile Scraper**  
  Access rich and detailed profile information without needing a browser or manual copy-pasting.
- **Reverse Email Lookup**  
  Instantly check if an email is linked to a public LinkedIn profile—perfect for verification or enrichment tasks.
- **LinkedIn Viewer / Profile Viewer**  
  Quickly explore and analyze public LinkedIn profiles, just like a regular user—but automated.
- **Exporting Comments & Reactions**  
  Grab post interactions to better understand sentiment, audience behavior, or engagement trends.
- **LinkedIn Automation**  
  Build smarter, more reliable tools that interact with LinkedIn data—without the fragility of browser scraping.
- **SerpAPI Alternatives**  
  Get LinkedIn data directly from the source—no need to scrape search engine result pages or deal with CAPTCHAs.

---

## 🏁 Final Thoughts

At its core, **LinkdAPI** is more than just an API—it's a reliable engine for anyone building tools that require access to public LinkedIn data. As the #1 unofficial **LinkedIn scraper** for developers, it empowers you to build robust **LinkedIn automation**, perform advanced **reverse email lookups**, and create scalable **LinkedIn profile viewer** solutions with confidence.

If you're crafting a high-performance **LinkedIn data extractor**, a deep-dive **LinkedIn profile scraper**, or a lightweight **LinkedIn viewer**, **LinkdAPI** delivers the power, performance, and flexibility to do it all—without the headaches of traditional scraping.

---

## 🔗 Useful Links

- [LinkdAPI.com](https://linkdapi.com/)
- [API Documentation](https://linkdapi.com/docs/intro)
- [Help Center](https://linkdapi.com/help-center)
- [Roadmap](https://linkdapi.com/roadmap)

---

## 📜 License

**MIT License** – Use responsibly. This tool is intended strictly for **research and educational purposes**.
