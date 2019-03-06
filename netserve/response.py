'''
Created on Wednesday 06/03/2019

@author: yaztown
'''

from http.server import BaseHTTPRequestHandler
from email.header import Header
from urllib.parse import quote, urlparse, unquote

responses = BaseHTTPRequestHandler.responses

import re
import json
import sys
import datetime
import uuid
import decimal 

_charset_from_content_type_re = re.compile(r';\s*charset=(?P<charset>[^\s;]+)', re.RegexFlag.IGNORECASE)


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if issubclass(type(s), str):
        return s
    try:
        if not issubclass(type(s), str):
            if isinstance(s, bytes):
                s = str(s, encoding, errors)
            elif hasattr(s, '__unicode__') or hasattr(s, '__str__'):
                s = str(s)
            else:
                s = str(bytes(s), encoding, errors)
        else:
            # Note: We use .decode() here, instead of six.text_type(s, encoding,
            # errors), so that if s is a SafeBytes, it ends up being a
            # SafeText at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
            raise UnicodeDecodeError(s, *e.args)
    return s

force_str = force_text


def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if isinstance(s, memoryview):
        return bytes(s)
    if not isinstance(s, str):
        try:
            return str(s).encode(encoding)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return b' '.join(force_bytes(arg, encoding, strings_only, errors)
                                 for arg in s)
            return str(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


def iri_to_uri(iri):
    """
    Convert an Internationalized Resource Identifier (IRI) portion to a URI
    portion that is suitable for inclusion in a URL.

    This is the algorithm from section 3.1 of RFC 3987.  However, since we are
    assuming input is either UTF-8 or unicode already, we can simplify things a
    little from the full method.

    Takes an IRI in UTF-8 bytes (e.g. '/I \xe2\x99\xa5 Django/') or unicode
    (e.g. '/I ♥ Django/') and returns ASCII bytes containing the encoded result
    (e.g. '/I%20%E2%99%A5%20Django/').
    """
    # The list of safe characters here is constructed from the "reserved" and
    # "unreserved" characters specified in sections 2.2 and 2.3 of RFC 3986:
    #     reserved    = gen-delims / sub-delims
    #     gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    #     sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
    #                   / "*" / "+" / "," / ";" / "="
    #     unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    # Of the unreserved characters, urllib.quote already considers all but
    # the ~ safe.
    # The % character is also added to the list of safe characters here, as the
    # end of section 3.1 of RFC 3987 specifically mentions that % must not be
    # converted.
    if iri is None:
        return iri
    return quote(force_bytes(iri), safe=b"/#%[]=:;$&()+,!?*@'~")



class SuspiciousOperation(Exception):
    """The user did something suspicious"""
    pass

class DisallowedRedirect(SuspiciousOperation):
    """Redirect to scheme not in allowed list"""
    pass




class BadHeaderError(ValueError):
    pass

class HttpResponseBase(object):
    """
    An HTTP response base class with dictionary-accessed headers.

    This class doesn't handle content. It should not be used directly.
    Use the HttpResponse and StreamingHttpResponse subclasses instead.
    """

    status_code = 200
    DEFAULT_CONTENT_TYPE='text/html'
    DEFAULT_CHARSET = 'utf-8'

    def __init__(self, content_type=None, status=None, reason=None, charset=None):
        # _headers is a mapping of the lower-case name to the original case of
        # the header (required for working with legacy systems) and the header
        # value. Both the name of the header and its value are ASCII strings.
        self._headers = {}
        self._closable_objects = []
        # This parameter is set by the handler. It's necessary to preserve the
        # historical behavior of request_finished.
        self._handler_class = None
#         self.cookies = SimpleCookie()
        self.closed = False
        if status is not None:
            try:
                self.status_code = int(status)
            except (ValueError, TypeError):
                raise TypeError('HTTP status code must be an integer.')

            if not 100 <= self.status_code <= 599:
                raise ValueError('HTTP status code must be an integer from 100 to 599.')
        self._reason_phrase = reason
        self._charset = charset
        if content_type is None:
            content_type = '{}; charset={}'.format(self.DEFAULT_CONTENT_TYPE,
                                               self.charset)
        self['Content-Type'] = content_type

    @property
    def reason_phrase(self):
        if self._reason_phrase is not None:
            return self._reason_phrase
        # Leave self._reason_phrase unset in order to use the default
        # reason phrase for status code.
        return responses.get(self.status_code, 'Unknown Status Code')

    @reason_phrase.setter
    def reason_phrase(self, value):
        self._reason_phrase = value

    @property
    def charset(self):
        if self._charset is not None:
            return self._charset
        content_type = self.get('Content-Type', '')
        matched = _charset_from_content_type_re.search(content_type)
        if matched:
            # Extract the charset and strip its double quotes
            return matched.group('charset').replace('"', '')
        return self.DEFAULT_CHARSET

    @charset.setter
    def charset(self, value):
        self._charset = value

    def serialize_headers(self):
        """HTTP headers as a bytestring."""
        def to_bytes(val, encoding):
            return val if isinstance(val, bytes) else val.encode(encoding)

        headers = [
            (b': '.join([to_bytes(key, 'ascii'), to_bytes(value, 'latin-1')]))
            for key, value in self._headers.values()
        ]
        return b'\r\n'.join(headers)

    __bytes__ = serialize_headers

    @property
    def _content_type_for_repr(self):
        return ', "%s"' % self['Content-Type'] if 'Content-Type' in self else ''

    def _convert_to_charset(self, value, charset, mime_encode=False):
        """Converts headers key/value to ascii/latin-1 native strings.

        `charset` must be 'ascii' or 'latin-1'. If `mime_encode` is True and
        `value` can't be represented in the given charset, MIME-encoding
        is applied.
        """
        if not isinstance(value, (bytes, str)):
            value = str(value)
        if ((isinstance(value, bytes) and (b'\n' in value or b'\r' in value)) or
                isinstance(value, str) and ('\n' in value or '\r' in value)):
            raise BadHeaderError("Header values can't contain newlines (got %r)" % value)
        try:
            if isinstance(value, str):
                # Ensure string is valid in given charset
                value.encode(charset)
            else:
                # Convert bytestring using given charset
                value = value.decode(charset)
        except UnicodeError as e:
            if mime_encode:
                # Wrapping in str() is a workaround for #12422 under Python 2.
                value = str(Header(value, 'utf-8', maxlinelen=sys.maxsize).encode())
            else:
                e.reason += ', HTTP response headers must be in %s format' % charset
                raise
        return value

    def __setitem__(self, header, value):
        header = self._convert_to_charset(header, 'ascii')
        value = self._convert_to_charset(value, 'latin-1', mime_encode=True)
        self._headers[header.lower()] = (header, value)

    def __delitem__(self, header):
        try:
            del self._headers[header.lower()]
        except KeyError:
            pass

    def __getitem__(self, header):
        return self._headers[header.lower()][1]

    def has_header(self, header):
        """Case-insensitive check for a header."""
        return header.lower() in self._headers

    __contains__ = has_header

    def items(self):
        return self._headers.values()

    def get(self, header, alternate=None):
        return self._headers.get(header.lower(), (None, alternate))[1]

#     def set_cookie(self, key, value='', max_age=None, expires=None, path='/',
#                    domain=None, secure=False, httponly=False):
#         """
#         Sets a cookie.
# 
#         ``expires`` can be:
#         - a string in the correct format,
#         - a naive ``datetime.datetime`` object in UTC,
#         - an aware ``datetime.datetime`` object in any time zone.
#         If it is a ``datetime.datetime`` object then ``max_age`` will be calculated.
#         """
#         value = force_str(value)
#         self.cookies[key] = value
#         if expires is not None:
#             if isinstance(expires, datetime.datetime):
#                 if timezone.is_aware(expires):
#                     expires = timezone.make_naive(expires, timezone.utc)
#                 delta = expires - expires.utcnow()
#                 # Add one second so the date matches exactly (a fraction of
#                 # time gets lost between converting to a timedelta and
#                 # then the date string).
#                 delta = delta + datetime.timedelta(seconds=1)
#                 # Just set max_age - the max_age logic will set expires.
#                 expires = None
#                 max_age = max(0, delta.days * 86400 + delta.seconds)
#             else:
#                 self.cookies[key]['expires'] = expires
#         else:
#             self.cookies[key]['expires'] = ''
#         if max_age is not None:
#             self.cookies[key]['max-age'] = max_age
#             # IE requires expires, so set it if hasn't been already.
#             if not expires:
#                 self.cookies[key]['expires'] = cookie_date(time.time() +
#                                                            max_age)
#         if path is not None:
#             self.cookies[key]['path'] = path
#         if domain is not None:
#             self.cookies[key]['domain'] = domain
#         if secure:
#             self.cookies[key]['secure'] = True
#         if httponly:
#             self.cookies[key]['httponly'] = True

    def setdefault(self, key, value):
        """Sets a header unless it has already been set."""
        if key not in self:
            self[key] = value

#     def set_signed_cookie(self, key, value, salt='', **kwargs):
#         value = signing.get_cookie_signer(salt=key + salt).sign(value)
#         return self.set_cookie(key, value, **kwargs)

#     def delete_cookie(self, key, path='/', domain=None):
#         self.set_cookie(key, max_age=0, path=path, domain=domain,
#                         expires='Thu, 01-Jan-1970 00:00:00 GMT')

    # Common methods used by subclasses

    def make_bytes(self, value):
        """Turn a value into a bytestring encoded in the output charset."""
        # Per PEP 3333, this response body must be bytes. To avoid returning
        # an instance of a subclass, this function returns `bytes(value)`.
        # This doesn't make a copy when `value` already contains bytes.

        # Handle string types -- we can't rely on force_bytes here because:
        # - under Python 3 it attempts str conversion first
        # - when self._charset != 'utf-8' it re-encodes the content
        if isinstance(value, bytes):
            return bytes(value)
        if isinstance(value, str):
            return bytes(value.encode(self.charset))

        # Handle non-string types (#16494)
        return force_bytes(value, self.charset)

    # These methods partially implement the file-like object interface.
    # See https://docs.python.org/3/library/io.html#io.IOBase

    # The WSGI server must call this method upon completion of the request.
    # See http://blog.dscpl.com.au/2012/10/obligations-for-calling-close-on.html
    def close(self):
        for closable in self._closable_objects:
            try:
                closable.close()
            except Exception:
                pass
        self.closed = True
#         signals.request_finished.send(sender=self._handler_class)

    def write(self, content):
        raise IOError("This %s instance is not writable" % self.__class__.__name__)

    def flush(self):
        pass

    def tell(self):
        raise IOError("This %s instance cannot tell its position" % self.__class__.__name__)

    # These methods partially implement a stream-like object interface.
    # See https://docs.python.org/library/io.html#io.IOBase

    def readable(self):
        return False

    def seekable(self):
        return False

    def writable(self):
        return False

    def writelines(self, lines):
        raise IOError("This %s instance is not writable" % self.__class__.__name__)


class HttpResponse(HttpResponseBase):
    """
    An HTTP response class with a string as content.

    This content that can be read, appended to or replaced.
    """

    streaming = False

    def __init__(self, content=b'', *args, **kwargs):
        super(HttpResponse, self).__init__(*args, **kwargs)
        # Content is a bytestring. See the `content` property methods.
        self.content = content

    def __repr__(self):
        return '<%(cls)s status_code=%(status_code)d%(content_type)s>' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self._content_type_for_repr,
        }

    def serialize(self):
        """Full HTTP message, including headers, as a bytestring."""
        return self.serialize_headers() + b'\r\n\r\n' + self.content

    __bytes__ = serialize

    @property
    def content(self):
        return b''.join(self._container)

    @content.setter
    def content(self, value):
        # Consume iterators upon assignment to allow repeated iteration.
        if hasattr(value, '__iter__') and not isinstance(value, (bytes, str)):
            content = b''.join(self.make_bytes(chunk) for chunk in value)
            if hasattr(value, 'close'):
                try:
                    value.close()
                except Exception:
                    pass
        else:
            content = self.make_bytes(value)
        # Create a list of properly encoded bytestrings to support write().
        self._container = [content]

    def __iter__(self):
        return iter(self._container)

    def write(self, content):
        self._container.append(self.make_bytes(content))

    def tell(self):
        return len(self.content)

    def getvalue(self):
        return self.content

    def writable(self):
        return True

    def writelines(self, lines):
        for line in lines:
            self.write(line)


class StreamingHttpResponse(HttpResponseBase):
    """
    A streaming HTTP response class with an iterator as content.

    This should only be iterated once, when the response is streamed to the
    client. However, it can be appended to or replaced with a new iterator
    that wraps the original content (or yields entirely new content).
    """

    streaming = True

    def __init__(self, streaming_content=(), *args, **kwargs):
        super(StreamingHttpResponse, self).__init__(*args, **kwargs)
        # `streaming_content` should be an iterable of bytestrings.
        # See the `streaming_content` property methods.
        self.streaming_content = streaming_content

    @property
    def content(self):
        raise AttributeError(
            "This %s instance has no `content` attribute. Use "
            "`streaming_content` instead." % self.__class__.__name__
        )

    @property
    def streaming_content(self):
        return map(self.make_bytes, self._iterator)

    @streaming_content.setter
    def streaming_content(self, value):
        self._set_streaming_content(value)

    def _set_streaming_content(self, value):
        # Ensure we can never iterate on "value" more than once.
        self._iterator = iter(value)
        if hasattr(value, 'close'):
            self._closable_objects.append(value)

    def __iter__(self):
        return self.streaming_content

    def getvalue(self):
        return b''.join(self.streaming_content)


class FileResponse(StreamingHttpResponse):
    """
    A streaming HTTP response class optimized for files.
    """
    block_size = 4096

    def _set_streaming_content(self, value):
        if hasattr(value, 'read'):
            self.file_to_stream = value
            filelike = value
            if hasattr(filelike, 'close'):
                self._closable_objects.append(filelike)
            value = iter(lambda: filelike.read(self.block_size), b'')
        else:
            self.file_to_stream = None
        super(FileResponse, self)._set_streaming_content(value)


class HttpResponseRedirectBase(HttpResponse):
    allowed_schemes = ['http', 'https', 'ftp']

    def __init__(self, redirect_to, *args, **kwargs):
        super(HttpResponseRedirectBase, self).__init__(*args, **kwargs)
        self['Location'] = iri_to_uri(redirect_to)
        parsed = urlparse(force_text(redirect_to))
        if parsed.scheme and parsed.scheme not in self.allowed_schemes:
            raise DisallowedRedirect("Unsafe redirect to URL with protocol '%s'" % parsed.scheme)

    url = property(lambda self: self['Location'])

    def __repr__(self):
        return '<%(cls)s status_code=%(status_code)d%(content_type)s, url="%(url)s">' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self._content_type_for_repr,
            'url': self.url,
        }


class HttpResponseRedirect(HttpResponseRedirectBase):
    status_code = 302


class HttpResponsePermanentRedirect(HttpResponseRedirectBase):
    status_code = 301


class HttpResponseNotModified(HttpResponse):
    status_code = 304

    def __init__(self, *args, **kwargs):
        super(HttpResponseNotModified, self).__init__(*args, **kwargs)
        del self['content-type']

    @HttpResponse.content.setter
    def content(self, value):
        if value:
            raise AttributeError("You cannot set content to a 304 (Not Modified) response")
        self._container = []


class HttpResponseBadRequest(HttpResponse):
    status_code = 400


class HttpResponseNotFound(HttpResponse):
    status_code = 404


class HttpResponseForbidden(HttpResponse):
    status_code = 403


class HttpResponseNotAllowed(HttpResponse):
    status_code = 405

    def __init__(self, permitted_methods, *args, **kwargs):
        super(HttpResponseNotAllowed, self).__init__(*args, **kwargs)
        self['Allow'] = ', '.join(permitted_methods)

    def __repr__(self):
        return '<%(cls)s [%(methods)s] status_code=%(status_code)d%(content_type)s>' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self._content_type_for_repr,
            'methods': self['Allow'],
        }


class HttpResponseGone(HttpResponse):
    status_code = 410


class HttpResponseServerError(HttpResponse):
    status_code = 500


class Http404(Exception):
    pass


def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The concept is defined in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def _get_duration_components(duration):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds


def duration_iso_string(duration):
    if duration < datetime.timedelta(0):
        sign = '-'
        duration *= -1
    else:
        sign = ''

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = '.{:06d}'.format(microseconds) if microseconds else ""
    return '{}P{}DT{:02d}H{:02d}M{:02d}{}S'.format(sign, days, hours, minutes, seconds, ms)

class DjangoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)





class JsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    :param json_dumps_params: A dictionary of kwargs passed to json.dumps().
    """

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True,
                 json_dumps_params=None, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if json_dumps_params is None:
            json_dumps_params = {}
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder, **json_dumps_params)
        super(JsonResponse, self).__init__(content=data, **kwargs)
