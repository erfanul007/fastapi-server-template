from typing import Annotated

import nh3
from pydantic import AfterValidator

# --- Allowed HTML for safe messages ---
ALLOWED_TAGS = {"b", "i", "em", "strong", "a", "p", "br", "ul", "ol", "li", "img"}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "img": {"src", "alt"},
}

ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


def nh3_cleaner(html_content: str) -> str:
    html_content = html_content.strip()

    if not html_content:
        return ""

    return nh3.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
        strip_comments=True,
    )


SafeHTMLString = Annotated[str, AfterValidator(nh3_cleaner)]
