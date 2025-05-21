# Confluence Change Log Action

Forked from [Gershon-A/publish-release-to-confluence](https://github.com/Gershon-A/publish-release-to-confluence)

This fork updates a change log page in Confluence with the release notes for a particular release. Release notes are prepended to the change log page.

## Inputs

The action requires the following inputs:

| Name         | Description                                                                     | Required | Default |
|--------------|---------------------------------------------------------------------------------|----------|---------|
| `email`      | The email address associated with your Confluence account.                      | True     | -       |
| `api_token`  | The API token for your Confluence account.                                      | True     | -       |
| `host`       | The host of your Confluence instance.                                           | True     | -       |
| `space_key`  | The key of the Confluence space where the release page is located.              | True     | -       |
| `page_id`    | The id of the Confluence page to update. This page must already exist.          | True     | -       |
| `status`     | The status of the page to be updated.                                           | False    | current |
| `title`      | The title of the page to be updated.                                            | True     | -       |
| `repository` | The slug of the GitHub repository from which the release notes will be fetched. | True     | -       |
| `tag`        | The tag of the GitHub release from which the release notes will be fetched.     | True     | -       |

## Usage

To use this action in your GitHub workflow, add the following step:

```yaml
  update-release-notes:
    runs-on: ubuntu-latest
    steps:
      - name: Publish release notes to Confluence
        uses: snxd/confluence-change-log-action@main
        with:
          email: ${{ secrets.CONFLUENCE_EMAIL }}
          api_token: ${{ secrets.CONFLUENCE_API_TOKEN }}
          host: your-host.atlassian.net
          space_key: your-project-key
          page_id: ${{ secrets.CONFLUENCE_PAGE_ID }}
          title: Your App Change Log
          repository: ${{ github.repository }}
          tag: ${{ github.ref_name }}
```