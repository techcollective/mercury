class VtigerRouter(object):
    """
    The purpose of this class is to direct certain apps to sync and read
    with a particular db only. All other apps are directed to "default".

    db_to_app is a dict defining the special apps and the db they should read
    from and sync to.
    """
    app_to_db = {"vtiger": "vtiger"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.app_to_db:
            return self.app_to_db[model._meta.app_label]
        else:
            return "default"

    def allow_syncdb(self, db, model):
        if model._meta.app_label in self.app_to_db:
            return self.app_to_db[model._meta.app_label] == db
        elif db == "default":
            return True
        else:
            return False
