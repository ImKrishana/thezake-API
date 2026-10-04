ANIME_QUERY = """
query ($id: Int, $search: String) {
  Media(id: $id, type: ANIME, search: $search) {
    id
    idMal
    title { romaji english native }
    type
    format
    status(version: 2)
    description(asHtml: false)
    startDate { year month day }
    endDate { year month day }
    season
    seasonYear
    episodes
    duration
    countryOfOrigin
    source
    hashtag
    trailer { id site thumbnail }
    updatedAt
    coverImage { large }
    bannerImage
    genres
    synonyms
    averageScore
    meanScore
    popularity
    trending
    favourites
    tags { name description rank }
    studios { nodes { name siteUrl } }
    siteUrl
    externalLinks { url site }
    nextAiringEpisode { airingAt timeUntilAiring episode }
    relations {
      edges {
        relationType
        node {
          id
          title { romaji english native }
          format
          status
          source
          averageScore
          siteUrl
        }
      }
    }
    characters {
      edges {
        role
        node {
          id
          name { full native }
          siteUrl
          image { large }
        }
      }
    }
    reviews {
      nodes {
        summary
        rating
        score
        siteUrl
        user { name }
      }
    }
  }
}
"""

CHARACTER_QUERY = """
query ($id: Int, $search: String) {
  Character(id: $id, search: $search) {
    id
    name { first last full native }
    siteUrl
    image { large }
    description(asHtml: false)
  }
}
"""

MANGA_QUERY = """
query ($id: Int, $search: String) {
  Media(id: $id, type: MANGA, search: $search) {
    id
    idMal
    title { romaji english native }
    type
    format
    status(version: 2)
    description(asHtml: false)
    startDate { year month day }
    endDate { year month day }
    chapters
    volumes
    countryOfOrigin
    source
    updatedAt
    coverImage { large }
    bannerImage
    genres
    synonyms
    averageScore
    meanScore
    popularity
    favourites
    tags { name description rank }
    siteUrl
    externalLinks { url site }
    relations {
      edges {
        relationType
        node {
          id
          title { romaji english native }
          format
          status
          source
          averageScore
          siteUrl
        }
      }
    }
  }
}
"""
