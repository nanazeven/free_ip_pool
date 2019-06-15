from manage import Manage


def main():
    try:
        manage = Manage()
        manage.start()
    except:
        print('pool run error.')

if __name__ == '__main__':
    main()
