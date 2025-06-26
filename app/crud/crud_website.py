from app.api.deps import db_dependency, user_dependency
from app.models.website import Website
from app.schemas.website import WebsiteRequest


def create_website(website: WebsiteRequest, db: db_dependency, user: user_dependency, scraped_website):
    new_website = Website(
        url=website.url,
        owner_id=user.get("id"),
        title=scraped_website["title"],
        chunks=scraped_website["chunks"]
    )

    db.add(new_website)
    db.commit()
    db.refresh(new_website)

    return new_website

def get_websites(db: db_dependency, user: user_dependency):
    websites = db.query(Website).filter(Website.owner_id == user.get("id")).all()
    return websites

