ThisBuild / scalaVersion := "3.3.7"

lazy val commonSettings = Seq(
    scalaVersion := "3.3.7",
    Test / parallelExecution := false,
)



lazy val armlet = (project in file("armlet"))
  .settings(commonSettings, guiDeps,
    libraryDependencies += "org.scala-lang.modules" %% "scala-parser-combinators" % "2.4.0",
  )
  .dependsOn(minilog)


lazy val guiDeps = Seq(
  libraryDependencies += ("org.scala-lang.modules" %% "scala-swing" % "3.0.0"),
)


lazy val minilog = (project in file("minilog"))
  .settings(commonSettings, guiDeps,
  )
