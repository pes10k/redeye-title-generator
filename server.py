import motor
import config
import redeye.controllers
import redeye.newssources
import tornado
import tornado.web

mongo = config.mongo
db = motor.MotorClient(mongo['host'], mongo['port']).open_sync()[mongo['database']]

routes = [(r'/' + s, redeye.controllers.MainController) for s in redeye.newssources.sources.keys()]
routes = ((r'/(.*)', redeye.controllers.MainController),)

application = tornado.web.Application(routes, db=db, debug=config.debug,
                                      static_path=config.static_dir)
application.listen(8080)
tornado.ioloop.IOLoop.instance().start()
