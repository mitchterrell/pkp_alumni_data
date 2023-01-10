import os
import sys
import http.client
import json

access_token = "CMT0R-q0dcs6i9ZZ0fGmpBtULQGLIFsTMDwizgZZU30BKLb8A1hLoEgwjuCISbE3nDfDXqVmX-d-cRzJirep9y0C6yYehEZgX0JlustCbTtMf7EGvMxEgvdwMJ1LnVUU"


def json_pretty_print(to_print):
    parsed = json.loads(to_print)
    print(json.dumps(parsed, indent=4))


def surv_monk_get(to_get):
    conn = http.client.HTTPSConnection("api.surveymonkey.com")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    conn.request("GET", to_get, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data


def surv_monk_set(url, payload):
    conn = http.client.HTTPSConnection("api.surveymonkey.com")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    conn.request("POST", url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data


def make_survey_folder(fldr_name):
    url = "/v3/survey_folders"
    payload = '{"title":"' + fldr_name + '"}'
    dat_back = surv_monk_set(url, payload)
    dat_str = dat_back.decode("utf-8")
    if "error" in dat_str:
        json_pretty_print(dat_str)
        return -1
    else:
        dat_back_json = json.loads(dat_str)
        print(f"ID Found: {dat_back_json['id']}")
        return id


def build_survey(fldr_id):
    url = "/v3/surveys"
    payload = """{
  "title": "Example Survey",
  "folder_id": "%s"
  "pages": [
    {
      "title": "My First Page",
      "description": "Page description",
      "position": 1,
      "questions": [
        {
          "family": "single_choice",
          "subtype": "vertical",
          "answers": {
            "choices": [
              {
                "text": "Apple",
                "position": 1
              },
              {
                "text": "Orange",
                "position": 2
              },
              {
                "text": "Banana",
                "position": 3
              }
            ]
          },
          "headings": [
            {
              "heading": "What is your favourite fruit?"
            }
          ],
          "position": 1
        }
      ]
    }
  ]
}""" % (
        fldr_id
    )

    dat_back = surv_monk_set(url, payload)
    dat_str = dat_back.decode("utf-8")
    json_pretty_print(dat_str)


def main():

    print("Hello World!")
    fldr_id = make_survey_folder("Test 1")
    build_survey(fldr_id)

    # conn = http.client.HTTPSConnection("api.surveymonkey.com")
    # headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    # conn.request("GET", "/v3/surveys", headers=headers)
    # res = conn.getresponse()
    # data = res.read()

    # json_pretty_print(data.decode("utf-8"))

    # print(data.decode("utf-8"))


if __name__ == "__main__":
    main()
