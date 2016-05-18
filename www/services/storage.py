import uuid, StringIO, csv
import www.libs.cloudstorage as gcs
import cgi

from google.appengine.ext import blobstore, deferred

EACCESS_TEMP_FILENAME_TEMPLATE = "hackillinois2016eaccess-%d.tmp.csv"
BUS_TEMP_FILENAME_TEMPLATE = "hackillinois2016buses-%d.tmp.csv"
EACCESS_FILENAME = "hackillinois2016eaccess.csv"
BUS_FILENAME = "hackillinois2016buses.csv"
ATTENDEE_TEMP_FILENAME_TEMPLATE = "hackillinois2016attendees-%d.tmp.csv"
ATTENDEE_FILENAME = "hackillinois2016attendees.csv"

class FileValidationException(Exception):
    """
    Base class representing an issue related to the file validation
    """

class BadFileType(FileValidationException):
    """
    Raised when a file has an unanticipated or unacceptable file type
    """
    pass

class FileSizeExceeded(FileValidationException):
    """
    Raised when a file exceeds the maximum upload size
    """
    pass

class StorageService(object):
    """
    The StorageService implements functionality required to write and delete
    files help in Google Cloud Store buckets. Fetching these files should be done
    via the google.appengine.ext.blobstore_handlers.BlobstoreDownloadHandler
    """

    _CONFIG = None
    _CONFIG_KEY = 'services.storage'
    _GCS_PREFIX = '/gs'

    # TODO move this into configuration in the future
    MAX_FILE_UPLOAD_SIZE_BYTES = 2 * 1000000

    def __init__(self, app):
        if not StorageService._CONFIG:
            StorageService._CONFIG = app.config[StorageService._CONFIG_KEY]

    def __verify_file_type(self, data, mime_types):
        """
        Ensures that the provided data (file) is of one of the types
        specified in :mime_types:

        args:
            data: a cgi.FieldStorage instance
            mime_types: a list of acceptable MIME types
        raises:
            BadFileType
        """
        if data is None or not isinstance(data, cgi.FieldStorage):
            raise ValueError("Cannot process provided data (expected cgi.FieldStorage): %r" % data)

        if not data.type in mime_types:
            raise BadFileType("Data was of type %s but only data of types %r are allowed" % (data.type, mime_types))

    def __verify_file_size(self, data):
        """
        Ensures that the provided data (file) is no larger
        than the maximum file upload size

        args:
            data: a cgi.FieldStorage instance
        raises:
            FileSizeExceeded
        """
        if data is None or not isinstance(data, cgi.FieldStorage):
            raise ValueError("Cannot process provided data (expected cgi.FieldStorage): %r" % data)

        data.file.seek(0, 2)
        data_size = data.file.tell()
        data.file.seek(0)

        data_overage = data_size - StorageService.MAX_FILE_UPLOAD_SIZE_BYTES
        if data_overage > 0:
            raise FileSizeExceeded("Data exceeded maximum by %d bytes" % data_overage)

    def __set_filename(self, data, bucket, extension=''):
        """
        Ensures that the provided data (file) has a filename
        that will not collide with others in its bucket

        args:
            data: a cgi.FieldStorage instance
        """

        if data is None or not isinstance(data, cgi.FieldStorage):
            raise ValueError("Cannot set filename of provided data (expected cgi.FieldStorage): %r" % data)

        # every file that we upload must have a unique
        # identifier, so we create a uuid and overwrite the original name
        filename = uuid.uuid4().hex
        data.filename = "/%s/%s%s" % (bucket, filename, extension)

    def __get_bucket_filename(self, bucket, filename):
        """
        Ensures that the provided data (file) has a filename
        in its bucket
        """
        # every file that we upload must have a unique
        # identifier, so we create a uuid and overwrite the original name
        return "/%s/%s" % (bucket, filename)

    def __write_file(self, data):
        """
        Writes the provided data (file) to cloud storage. It is
        assumed that the filename of :data: is consistent with
        the result of __set_filename

        args:
            data: a cgi.FieldStorage instance
        """

        if data is None or not isinstance(data, cgi.FieldStorage):
            raise ValueError("Cannot write provided data (expected cgi.FieldStorage): %r" % data)

        contents = data.file.getvalue()
        try:
            # we try to write the contents of the data to
            # a new file in GCS
            with gcs.open(data.filename, content_type=data.type, mode='w') as file_stream:
                file_stream.write(contents)
                file_stream.close()
        except Exception, e:
            raise e
        finally:
            # data.file is a cStringIO instance, which means
            # that it must be closed to free the buffer
            data.file.close()

    def __get_blobstore_key(self, data):
        """
        Retrieves a blob-key for the provided data (file). It is
        assumed that the contents of :data: have already been
        written to GCS

        args:
            data: a cgi.FieldStorage instance
        returns:
            a string representing a blobstore key that can be used to access the file later
        """

        if data is None or not isinstance(data, cgi.FieldStorage):
            raise ValueError("Cannot retrieve key for provided data (expected cgi.FieldStorage): %r" % data)

        blobstore_filename = StorageService._GCS_PREFIX + data.filename
        return blobstore.create_gs_key(blobstore_filename)

    def __delete_file(self, blobstore_key):
        """
        Deletes a key from __BlobInfo__ and from the associated
        GCS bucket. No check is made to see if the provided key is valid

        args:
            blobstore_key: a valid blobstore key
        """
        blobstore.delete(blobstore_key)

    def _populate_dump(self, iterations, bucket, template, writer):
        for index in xrange(iterations):
            temp_filename = template % index
            temp_filename = self.__get_bucket_filename(bucket, temp_filename)

            # we try to write the contents of the data to
            # a new file in GCS
            with gcs.open(temp_filename, mode='r') as file_stream:
                csv_reader = csv.reader(iter(file_stream.readline, ''), delimiter=',', quotechar='"')
                for row in csv_reader:
                    writer.writerow(row)
                file_stream.close()

            # once we are done with a temp file, we remove it
            gcs.delete(temp_filename)


    def _save_buffer(self, bucket, filename, file_buffer):
        filename = self.__get_bucket_filename(bucket, filename)
        data = file_buffer.getvalue()

        try:
            # we try to write the contents of the data to
            # a new file in GCS
            with gcs.open(filename, content_type='text/csv', mode='w') as file_stream:
                file_stream.write(data)
                file_stream.close()
        except Exception, e:
            raise e
        finally:
            # file_buffer is a StringIO instance, which means
            # that it must be closed to free the buffer
            file_buffer.close()

    def save_resume(self, resume):
        """
        Saves a resume to the appropriate GCS bucket. The file-stream
        will be closed regardless of whether or not the resume is saved

        args:
            resume: a cgi.FieldStorage instance

        returns:
            A blobstore.BlobKey for the provided resume
        """

        resume_bucket = StorageService._CONFIG['resume_bucket']
        resume_types = ['application/pdf']
        extension = '.pdf'


        self.__verify_file_type(resume, resume_types)
        self.__verify_file_size(resume)
        self.__set_filename(resume, resume_bucket, extension)
        self.__write_file(resume)
        key = self.__get_blobstore_key(resume)

        return blobstore.blobstore.BlobKey(key)

    def save_temp_sponsor_dump(self, index, file_buffer):

        public_bucket = StorageService._CONFIG['public_bucket']
        filename = EACCESS_TEMP_FILENAME_TEMPLATE % index

        self._save_buffer(public_bucket, filename, file_buffer)

    def save_temp_bus_dump(self, index, file_buffer):

        public_bucket = StorageService._CONFIG['public_bucket']
        filename = BUS_TEMP_FILENAME_TEMPLATE % index

        self._save_buffer(public_bucket, filename, file_buffer)

    def save_temp_attendee_dump(self, index, file_buffer):

        public_bucket = StorageService._CONFIG['public_bucket']
        filename = ATTENDEE_TEMP_FILENAME_TEMPLATE % index

        self._save_buffer(public_bucket, filename, file_buffer)

    def save_sponsor_dump(self, iterations):
        public_bucket = StorageService._CONFIG['public_bucket']
        file_buffer = StringIO.StringIO()

        writer = csv.writer(file_buffer)
        writer.writerow(["Role", "Email", "First Name", "Last Name", "Age", "Phone Number", "Gender", "School", "Major", "Graduation Year", "Employment Interests", "GitHub URL", "LinkedIn URL", "Personal URL", "Status", "Resume"])

        try:
            self._populate_dump(iterations, public_bucket, EACCESS_TEMP_FILENAME_TEMPLATE, writer)
        except Exception, e:
            raise e
            file_buffer.close()

        filename = EACCESS_FILENAME
        self._save_buffer(public_bucket, filename, file_buffer)

    def save_bus_dump(self, iterations):
        public_bucket = StorageService._CONFIG['public_bucket']
        file_buffer = StringIO.StringIO()

        writer = csv.writer(file_buffer)
        writer.writerow(["Email", "First Name", "Last Name", "Transportation"])

        try:
            self._populate_dump(iterations, public_bucket, BUS_TEMP_FILENAME_TEMPLATE, writer)
        except Exception, e:
            raise e
            file_buffer.close()

        filename = BUS_FILENAME
        self._save_buffer(public_bucket, filename, file_buffer)

    def save_attendee_dump(self, iterations):
        public_bucket = StorageService._CONFIG['public_bucket']
        file_buffer = StringIO.StringIO()

        writer = csv.writer(file_buffer)
        writer.writerow(["Email", "Initiative", "School", "Age", "Gender", "Major", "Graduation Year", "Meals"])

        try:
            self._populate_dump(iterations, public_bucket, ATTENDEE_TEMP_FILENAME_TEMPLATE, writer)
        except Exception, e:
            raise e
            file_buffer.close()

        filename = ATTENDEE_FILENAME
        self._save_buffer(public_bucket, filename, file_buffer)

    # this is an example of how to read a csv line-by-line
    # as input into, for example, a mail merge
    # def open_lob_csv(self, iteration):
    #     public_bucket = StorageService._CONFIG['public_bucket']
    #     filename = self.__get_bucket_filename(public_bucket, 'lob_codes_'+str(iteration)+'.csv')
    #
    #     file_stream = gcs.open(filename, mode='r')
    #     csv_reader = csv.reader(iter(file_stream.readline, ''), delimiter=',', quotechar='"')
    #     return csv_reader

    def delete(self, blobstore_key):
        """
        Deletes a file from GCS. No check is made to see if
        the provided key is valid

        args:
            blobstore_key: a valid blobstore key
        """
        self.__delete_file(blobstore_key)
