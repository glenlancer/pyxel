# pyxel
A python implementation of Axel

## Basic Description
This implementation aims to be run on Linux only.

### How it works

axel_new -> axel_open -> axel_start -> axel_do ->  axel_close

### Redirections in HTTP

URL redirections, also known as URL forwarding, is a technique to give more than one URL address to a page, a form, or a whole Web site/application. HTTP has a special kind of response, called a _HTTP redirect_, for this opersion.

Redirects accomplish numerous goals:

- Temporary redirects during site maintenance or downtime.
- Permanent redirects to perserve existing links/bookmarks after changing the site's URLs, progress pages when uploading a file, etc.

**Principle**
In Http, redirection is triggered by a server sending a special redirect response to a request. Redirect responses have status codes that start with 3, and a Location header holding the URL to redirect to.

There are several types of redirects, sorted into three categories:

1. Permanent redirections.
2. Temporary redirections.
3. Special redirections.

In Nginx, you create a specific server block for the content you want to redirect:

```
server {
    listen 80;
    server_name example.com;
    return 301 $scheme://www.example.com$request_uri;
}
```

To apply a redirect to a directory or only certain pages, use the `rewrite` directive:

```
rewrite ^/images/(.*)$ https://images.example.com/$1 redirect;
rewrite ^/images/(.*)$ https://images.example.com/$1 permanent;
```