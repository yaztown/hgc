'''
Created on Tuesday 05/03/2019

@author: yaztown
'''


class HttpRequest(object):
    """A basic HTTP request."""

    # The encoding used in GET/POST dicts. None means use default setting.
    _encoding = None
    _upload_handlers = []

    def __init__(self):
        # WARNING: The `WSGIRequest` subclass doesn't call `super`.
        # Any variable assignment made here should also happen in
        # `WSGIRequest.__init__()`.

        self.header = {}
        self.GET = {} #QueryDict(mutable=True)
        self.POST = {} #QueryDict(mutable=True)
#         self.COOKIES = {}
#         self.META = {}
#         self.FILES = MultiValueDict()

        self.path = ''
        self.path_info = ''
        self.method = None
#         self.resolver_match = None
        self._post_parse_error = False
        self.content_type = None
        self.content_params = None

    def __repr__(self):
        if self.method is None or not self.get_full_path():
            return '<{}>'.format(self.__class__.__name__)
        return '<{}: {} {}>'.format(self.__class__.__name__, self.method, self.get_full_path())
        

    def _get_raw_host(self):
        """
        Return the HTTP host using the environment or request headers. Skip
        allowed hosts protection, so may return an insecure host.
        """
        # We try three options, in order of decreasing preference.
        if settings.USE_X_FORWARDED_HOST and (
                'HTTP_X_FORWARDED_HOST' in self.META):
            host = self.META['HTTP_X_FORWARDED_HOST']
        elif 'HTTP_HOST' in self.META:
            host = self.META['HTTP_HOST']
        else:
            # Reconstruct the host using the algorithm from PEP 333.
            host = self.META['SERVER_NAME']
            server_port = self.get_port()
            if server_port != ('443' if self.is_secure() else '80'):
                host = '%s:%s' % (host, server_port)
        return host

    def get_host(self):
        """Return the HTTP host using the environment or request headers."""
        host = self._get_raw_host()

        # Allow variants of localhost if ALLOWED_HOSTS is empty and DEBUG=True.
        allowed_hosts = settings.ALLOWED_HOSTS
        if settings.DEBUG and not allowed_hosts:
            allowed_hosts = ['localhost', '127.0.0.1', '[::1]']

        domain, port = split_domain_port(host)
        if domain and validate_host(domain, allowed_hosts):
            return host
        else:
            msg = "Invalid HTTP_HOST header: %r." % host
            if domain:
                msg += " You may need to add %r to ALLOWED_HOSTS." % domain
            else:
                msg += " The domain name provided is not valid according to RFC 1034/1035."
            raise DisallowedHost(msg)

    def get_port(self):
        """Return the port number for the request as a string."""
        if settings.USE_X_FORWARDED_PORT and 'HTTP_X_FORWARDED_PORT' in self.META:
            port = self.META['HTTP_X_FORWARDED_PORT']
        else:
            port = self.META['SERVER_PORT']
        return str(port)

    def get_full_path(self, force_append_slash=False):
        # RFC 3986 requires query string arguments to be in the ASCII range.
        # Rather than crash if this doesn't happen, we encode defensively.
        return '%s%s%s' % (
            escape_uri_path(self.path),
            '/' if force_append_slash and not self.path.endswith('/') else '',
            ('?' + iri_to_uri(self.META.get('QUERY_STRING', ''))) if self.META.get('QUERY_STRING', '') else ''
        )

    def get_signed_cookie(self, key, default=RAISE_ERROR, salt='', max_age=None):
        """
        Attempts to return a signed cookie. If the signature fails or the
        cookie has expired, raises an exception... unless you provide the
        default argument in which case that value will be returned instead.
        """
        try:
            cookie_value = self.COOKIES[key]
        except KeyError:
            if default is not RAISE_ERROR:
                return default
            else:
                raise
        try:
            value = signing.get_cookie_signer(salt=key + salt).unsign(
                cookie_value, max_age=max_age)
        except signing.BadSignature:
            if default is not RAISE_ERROR:
                return default
            else:
                raise
        return value

    def get_raw_uri(self):
        """
        Return an absolute URI from variables available in this request. Skip
        allowed hosts protection, so may return insecure URI.
        """
        return '{scheme}://{host}{path}'.format(
            scheme=self.scheme,
            host=self._get_raw_host(),
            path=self.get_full_path(),
        )

    def build_absolute_uri(self, location=None):
        """
        Builds an absolute URI from the location and the variables available in
        this request. If no ``location`` is specified, the absolute URI is
        built on ``request.get_full_path()``. Anyway, if the location is
        absolute, it is simply converted to an RFC 3987 compliant URI and
        returned and if location is relative or is scheme-relative (i.e.,
        ``//example.com/``), it is urljoined to a base URL constructed from the
        request variables.
        """
        if location is None:
            # Make it an absolute url (but schemeless and domainless) for the
            # edge case that the path starts with '//'.
            location = '//%s' % self.get_full_path()
        bits = urlsplit(location)
        if not (bits.scheme and bits.netloc):
            current_uri = '{scheme}://{host}{path}'.format(scheme=self.scheme,
                                                           host=self.get_host(),
                                                           path=self.path)
            # Join the constructed URL with the provided location, which will
            # allow the provided ``location`` to apply query strings to the
            # base path as well as override the host, if it begins with //
            location = urljoin(current_uri, location)
        return iri_to_uri(location)

    def _get_scheme(self):
        """
        Hook for subclasses like WSGIRequest to implement. Returns 'http' by
        default.
        """
        return 'http'

    @property
    def scheme(self):
        if settings.SECURE_PROXY_SSL_HEADER:
            try:
                header, value = settings.SECURE_PROXY_SSL_HEADER
            except ValueError:
                raise ImproperlyConfigured(
                    'The SECURE_PROXY_SSL_HEADER setting must be a tuple containing two values.'
                )
            if self.META.get(header) == value:
                return 'https'
        return self._get_scheme()

    def is_secure(self):
        return self.scheme == 'https'

    def is_ajax(self):
        return self.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, val):
        """
        Sets the encoding used for GET/POST accesses. If the GET or POST
        dictionary has already been created, it is removed and recreated on the
        next access (so that it is decoded correctly).
        """
        self._encoding = val
        if hasattr(self, 'GET'):
            del self.GET
        if hasattr(self, '_post'):
            del self._post

    def _initialize_handlers(self):
        self._upload_handlers = [uploadhandler.load_handler(handler, self)
                                 for handler in settings.FILE_UPLOAD_HANDLERS]

    @property
    def upload_handlers(self):
        if not self._upload_handlers:
            # If there are no upload handlers defined, initialize them from settings.
            self._initialize_handlers()
        return self._upload_handlers

    @upload_handlers.setter
    def upload_handlers(self, upload_handlers):
        if hasattr(self, '_files'):
            raise AttributeError("You cannot set the upload handlers after the upload has been processed.")
        self._upload_handlers = upload_handlers

    def parse_file_upload(self, META, post_data):
        """Returns a tuple of (POST QueryDict, FILES MultiValueDict)."""
        self.upload_handlers = ImmutableList(
            self.upload_handlers,
            warning="You cannot alter upload handlers after the upload has been processed."
        )
        parser = MultiPartParser(META, post_data, self.upload_handlers, self.encoding)
        return parser.parse()

    @property
    def body(self):
        if not hasattr(self, '_body'):
            if self._read_started:
                raise RawPostDataException("You cannot access body after reading from request's data stream")

            # Limit the maximum request data size that will be handled in-memory.
            if (settings.DATA_UPLOAD_MAX_MEMORY_SIZE is not None and
                    int(self.META.get('CONTENT_LENGTH') or 0) > settings.DATA_UPLOAD_MAX_MEMORY_SIZE):
                raise RequestDataTooBig('Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE.')

            try:
                self._body = self.read()
            except IOError as e:
                six.reraise(UnreadablePostError, UnreadablePostError(*e.args), sys.exc_info()[2])
            self._stream = BytesIO(self._body)
        return self._body

    def _mark_post_parse_error(self):
        self._post = QueryDict()
        self._files = MultiValueDict()
        self._post_parse_error = True

    def _load_post_and_files(self):
        """Populate self._post and self._files if the content-type is a form type"""
        if self.method != 'POST':
            self._post, self._files = QueryDict(encoding=self._encoding), MultiValueDict()
            return
        if self._read_started and not hasattr(self, '_body'):
            self._mark_post_parse_error()
            return

        if self.content_type == 'multipart/form-data':
            if hasattr(self, '_body'):
                # Use already read data
                data = BytesIO(self._body)
            else:
                data = self
            try:
                self._post, self._files = self.parse_file_upload(self.META, data)
            except MultiPartParserError:
                # An error occurred while parsing POST data. Since when
                # formatting the error the request handler might access
                # self.POST, set self._post and self._file to prevent
                # attempts to parse POST data again.
                # Mark that an error occurred. This allows self.__repr__ to
                # be explicit about it instead of simply representing an
                # empty POST
                self._mark_post_parse_error()
                raise
        elif self.content_type == 'application/x-www-form-urlencoded':
            self._post, self._files = QueryDict(self.body, encoding=self._encoding), MultiValueDict()
        else:
            self._post, self._files = QueryDict(encoding=self._encoding), MultiValueDict()

    def close(self):
        if hasattr(self, '_files'):
            for f in chain.from_iterable(l[1] for l in self._files.lists()):
                f.close()

    # File-like and iterator interface.
    #
    # Expects self._stream to be set to an appropriate source of bytes by
    # a corresponding request subclass (e.g. WSGIRequest).
    # Also when request data has already been read by request.POST or
    # request.body, self._stream points to a BytesIO instance
    # containing that data.

    def read(self, *args, **kwargs):
        self._read_started = True
        try:
            return self._stream.read(*args, **kwargs)
        except IOError as e:
            six.reraise(UnreadablePostError, UnreadablePostError(*e.args), sys.exc_info()[2])

    def readline(self, *args, **kwargs):
        self._read_started = True
        try:
            return self._stream.readline(*args, **kwargs)
        except IOError as e:
            six.reraise(UnreadablePostError, UnreadablePostError(*e.args), sys.exc_info()[2])

    def xreadlines(self):
        while True:
            buf = self.readline()
            if not buf:
                break
            yield buf

    __iter__ = xreadlines

    def readlines(self):
        return list(iter(self))


class Request(object):
    '''
    classdocs
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        pass

class Response(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        