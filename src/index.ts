import { PrismaClient } from "@prisma/client";
import express from "express";

const prisma = new PrismaClient();

const app = express();

app.use(express.json());

app.get("/user/:username", async (req, res) => {
  const user = await prisma.user.findUnique({
    where: {
      name: req.params.username,
    },
    rejectOnNotFound: false,
  });

  if (!user) {
    return res.sendStatus(404);
  }

  return res.status(200).send(user);
});

app.post("/register", async (req, res) => {
  try {
    const udata = await prisma.user.create({
      data: {
        name: req.body.name,
        guilds: {
          create: {
            name: (req.body.name as string) + "'s server",
          },
        },
      },
      include: {
        guilds: true,
      },
    });

    await prisma.channel.create({
      data: {
        name: "general",
        guildId: udata.guilds[0].id,
      },
    });

    res.status(200).send(udata);
  } catch (e) {
    console.error(e);
    res.sendStatus(500);
  }
});

app.get("/guilds/:name", async (req, res) => {
  const guilds = await prisma.user
    .findUnique({
      where: {
        name: req.params.name,
      },
    })
    .guilds({
      include: {
        channels: true,
      },
    });

  try {
    res.status(200).json({ data: guilds });
  } catch (e) {
    console.error(e);
    res.sendStatus(500);
  }
});

app.put("/join-guild/:guildId", async (req, res) => {
  try {
    await prisma.user.update({
      where: {
        name: req.body.name,
      },
      data: {
        guilds: {
          connect: {
            id: req.params.guildId,
          },
        },
      },
    });
    const guild = await prisma.guild.findUnique({
      where: {
        id: req.params.guildId,
      },
      include: {
        channels: true,
      },
    });
    res.status(200).send(guild);
  } catch (e) {
    console.error(e);
    res.sendStatus(500);
  }
});

app.post("/message/:channelId/:authorId", async (req, res) => {
  await prisma.message.create({
    data: {
      content: req.body.content,
      authorId: req.params.authorId,
      channelId: req.params.channelId,
    },
  });
  res.sendStatus(200);
});

app.get("/messages/:channelId", async (req, res) => {
  try {
    const msgs = await prisma.message.findMany({
      take: 10,
      where: {
        channelId: req.params.channelId,
      },
      include: {
        author: true,
      },
    });
    return res.status(200).send({ data: msgs });
  } catch (e) {
    console.error(e);
    res.status(500);
  }
});

app.listen(3000, () => {
  console.log(`Listening on port ${process.env.PORT ?? 3000}`);
});
