from manage import Manage


def main():
    try:
        manage = Manage()
        manage.start()
    except Exception as e:
        print('pool run error.',e)
# def main():
#     manage = Manage()
#     manage.start()

if __name__ == '__main__':
    main()
