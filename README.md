# USB Info leak

## required packages

* pytsk3 
  * decoding error (utf-8)발생 시 python 경로\__init__.py 75line 근처의 return decode('utf-8')을 cp949로 변경해주세요
* pyewf
  * cygwin 설치 후 https://github.com/libyal/libewf/wiki/Building 참조하여 설치하면 됩니당.
* TSKUtil
* Registry

## supported extensions

* E01
* raw

